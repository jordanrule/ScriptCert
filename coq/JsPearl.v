From Coq Require Import ZArith List.
Import ListNotations.
Open Scope Z_scope.

Inductive value : Type :=
| VNum : Z -> value
| VSome : value -> value
| VUndef : value.

Inductive pattern : Type :=
| PMNum : Z -> pattern
| PMSome : pattern
| PMUndef : pattern
| PMWild : pattern.

Definition pattern_matches (p : pattern) (v : value) : bool :=
  match p, v with
  | PMNum n1, VNum n2 => Z.eqb n1 n2
  | PMSome, VSome _ => true
  | PMUndef, VUndef => true
  | PMWild, _ => true
  | _, _ => false
  end.

Fixpoint select_branch_value (v : value) (branches : list (pattern * value)) (dflt : value) : value :=
  match branches with
  | [] => dflt
  | (p, rhs) :: tl => if pattern_matches p v then rhs else select_branch_value v tl dflt
  end.

Definition lift_binop (op : Z -> Z -> Z) (a b : value) : value :=
  match a, b with
  | VNum x, VNum y => VNum (op x y)
  | _, _ => VUndef
  end.

Definition lift_unop (op : Z -> Z) (a : value) : value :=
  match a with
  | VNum x => VNum (op x)
  | _ => VUndef
  end.

Definition opt_chain_value (a : value) : value :=
  match a with
  | VSome inner => inner
  | _ => VUndef
  end.

(* Tiny JavaScript-like expression language. *)
Inductive expr : Type :=
| ENum : Z -> expr
| EAdd : expr -> expr -> expr
| ESub : expr -> expr -> expr
| EMul : expr -> expr -> expr
| ENeg : expr -> expr
| ESome : expr -> expr
| EOptChain : expr -> expr
| EMatchConst : expr -> list (pattern * value) -> value -> expr.

Fixpoint eval (e : expr) : value :=
  match e with
  | ENum n => VNum n
  | EAdd a b => lift_binop Z.add (eval a) (eval b)
  | ESub a b => lift_binop Z.sub (eval a) (eval b)
  | EMul a b => lift_binop Z.mul (eval a) (eval b)
  | ENeg a => lift_unop Z.opp (eval a)
  | ESome a => VSome (eval a)
  | EOptChain a => opt_chain_value (eval a)
  | EMatchConst scrutinee branches dflt =>
      select_branch_value (eval scrutinee) branches dflt
  end.

(* Tiny stack machine target language. *)
Inductive instr : Type :=
| IPush : value -> instr
| IAdd : instr
| ISub : instr
| IMul : instr
| INeg : instr
| IMakeSome : instr
| IOptChain : instr
| IMatchConst : list (pattern * value) -> value -> instr.

Definition stack := list value.
Definition program := list instr.

Definition step (i : instr) (st : stack) : option stack :=
  match i, st with
  | IPush v, _ => Some (v :: st)
  | IAdd, x :: y :: st' => Some (lift_binop Z.add y x :: st')
  | ISub, x :: y :: st' => Some (lift_binop Z.sub y x :: st')
  | IMul, x :: y :: st' => Some (lift_binop Z.mul y x :: st')
  | INeg, x :: st' => Some (lift_unop Z.opp x :: st')
  | IMakeSome, x :: st' => Some (VSome x :: st')
  | IOptChain, x :: st' => Some (opt_chain_value x :: st')
  | IMatchConst branches dflt, x :: st' => Some (select_branch_value x branches dflt :: st')
  | _, _ => None
  end.

Fixpoint run (p : program) (st : stack) : option stack :=
  match p with
  | [] => Some st
  | i :: p' =>
      match step i st with
      | Some st' => run p' st'
      | None => None
      end
  end.

Fixpoint compile (e : expr) : program :=
  match e with
  | ENum n => [IPush (VNum n)]
  | EAdd a b => compile a ++ compile b ++ [IAdd]
  | ESub a b => compile a ++ compile b ++ [ISub]
  | EMul a b => compile a ++ compile b ++ [IMul]
  | ENeg a => compile a ++ [INeg]
  | ESome a => compile a ++ [IMakeSome]
  | EOptChain a => compile a ++ [IOptChain]
  | EMatchConst scrutinee branches dflt =>
      compile scrutinee ++ [IMatchConst branches dflt]
  end.

Lemma run_app : forall p q st st',
  run p st = Some st' ->
  run (p ++ q) st = run q st'.
Proof.
  induction p as [|i p IHp]; intros q st st' Hrun; simpl in *.
  - inversion Hrun; subst. reflexivity.
  - destruct (step i st) as [st1|] eqn:Hstep; try discriminate.
    eapply IHp in Hrun. exact Hrun.
Qed.

Theorem compile_correct_aux : forall e st,
  run (compile e) st = Some (eval e :: st).
Proof.
  induction e as [n|a IHa b IHb|a IHa b IHb|a IHa b IHb|a IHa|a IHa|a IHa|scrutinee IHs branches dflt];
    intros st; simpl.
  - reflexivity.
  - rewrite run_app with (st' := eval a :: st).
    2: exact (IHa st).
    rewrite run_app with (st' := eval b :: eval a :: st).
    2: exact (IHb (eval a :: st)).
    simpl. reflexivity.
  - rewrite run_app with (st' := eval a :: st).
    2: exact (IHa st).
    rewrite run_app with (st' := eval b :: eval a :: st).
    2: exact (IHb (eval a :: st)).
    simpl. reflexivity.
  - rewrite run_app with (st' := eval a :: st).
    2: exact (IHa st).
    rewrite run_app with (st' := eval b :: eval a :: st).
    2: exact (IHb (eval a :: st)).
    simpl. reflexivity.
  - rewrite run_app with (st' := eval a :: st).
    2: exact (IHa st).
    simpl. reflexivity.
  - rewrite run_app with (st' := eval a :: st).
    2: exact (IHa st).
    simpl. reflexivity.
  - rewrite run_app with (st' := eval a :: st).
    2: exact (IHa st).
    simpl. reflexivity.
  - rewrite run_app with (st' := eval scrutinee :: st).
    2: exact (IHs st).
    simpl. reflexivity.
Qed.

Theorem compile_correct : forall e,
  run (compile e) [] = Some [eval e].
Proof.
  intros e. exact (compile_correct_aux e []).
Qed.

