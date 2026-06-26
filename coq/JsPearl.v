From Coq Require Import ZArith List.
Import ListNotations.
Open Scope Z_scope.

(* Tiny JavaScript-like expression language. *)
Inductive expr : Type :=
| ENum : Z -> expr
| EAdd : expr -> expr -> expr
| ESub : expr -> expr -> expr
| EMul : expr -> expr -> expr
| ENeg : expr -> expr.

Fixpoint eval (e : expr) : Z :=
  match e with
  | ENum n => n
  | EAdd a b => eval a + eval b
  | ESub a b => eval a - eval b
  | EMul a b => eval a * eval b
  | ENeg a => - (eval a)
  end.

(* Tiny stack machine target language. *)
Inductive instr : Type :=
| IPush : Z -> instr
| IAdd : instr
| ISub : instr
| IMul : instr
| INeg : instr.

Definition stack := list Z.
Definition program := list instr.

Definition step (i : instr) (st : stack) : option stack :=
  match i, st with
  | IPush n, _ => Some (n :: st)
  | IAdd, x :: y :: st' => Some ((y + x) :: st')
  | ISub, x :: y :: st' => Some ((y - x) :: st')
  | IMul, x :: y :: st' => Some ((y * x) :: st')
  | INeg, x :: st' => Some ((- x) :: st')
  | IAdd, _ => None
  | ISub, _ => None
  | IMul, _ => None
  | INeg, _ => None
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
  | ENum n => [IPush n]
  | EAdd a b => compile a ++ compile b ++ [IAdd]
  | ESub a b => compile a ++ compile b ++ [ISub]
  | EMul a b => compile a ++ compile b ++ [IMul]
  | ENeg a => compile a ++ [INeg]
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
  induction e as [n|a IHa b IHb|a IHa b IHb|a IHa b IHb|a IHa]; intros st; simpl.
  - reflexivity.
  - rewrite run_app with (st' := [eval a]).
    2: exact (IHa st).
    rewrite run_app with (st' := [eval b; eval a]).
    2: exact (IHb (eval a :: st)).
    simpl. reflexivity.
  - rewrite run_app with (st' := [eval a]).
    2: exact (IHa st).
    rewrite run_app with (st' := [eval b; eval a]).
    2: exact (IHb (eval a :: st)).
    simpl. reflexivity.
  - rewrite run_app with (st' := [eval a]).
    2: exact (IHa st).
    rewrite run_app with (st' := [eval b; eval a]).
    2: exact (IHb (eval a :: st)).
    simpl. reflexivity.
  - rewrite run_app with (st' := [eval a]).
    2: exact (IHa st).
    simpl. reflexivity.
Qed.

Theorem compile_correct : forall e,
  run (compile e) [] = Some [eval e].
Proof.
  intros e. exact (compile_correct_aux e []).
Qed.

