import Mathlib

namespace Sbtq

/-- Dephasing: keep only the diagonal entries. -/
def dephase {ι : Type _} [DecidableEq ι] {α : Type _} [Zero α] (A : Matrix ι ι α) : Matrix ι ι α :=
  Matrix.diagonal (fun i => A i i)

/-- Entry-wise formula for dephase. -/
theorem dephase_apply {ι : Type _} [DecidableEq ι] {α : Type _} [Zero α]
    (A : Matrix ι ι α) (i j : ι) :
    dephase A i j = (if i = j then A i i else 0) := by
  by_cases h : i = j
  · subst h
    simp [dephase]
  · simp [dephase, h]

/-- Dephasing is idempotent. -/
theorem dephase_idem {ι : Type _} [DecidableEq ι] {α : Type _} [Zero α]
    (A : Matrix ι ι α) : dephase (dephase A) = dephase A := by
  ext i j
  by_cases h : i = j
  · subst h
    simp [dephase]
  · simp [dephase, h]

/-- Fixed points of dephase are exactly diagonal matrices. -/
theorem dephase_fixed_iff_exists_diagonal {ι : Type _} [DecidableEq ι] {α : Type _} [Zero α]
    (A : Matrix ι ι α) :
    dephase A = A ↔ ∃ v : ι → α, A = Matrix.diagonal v := by
  constructor
  · intro h
    refine ⟨fun i => A i i, ?_⟩
    have : Matrix.diagonal (fun i => A i i) = A := by simpa [dephase] using h
    exact this.symm
  · rintro ⟨v, rfl⟩
    ext i j
    by_cases h : i = j
    · subst h
      simp [dephase]
    · simp [dephase, h]

/-- d=2 example: idempotence for ℂ matrices. -/
example (A : Matrix (Fin 2) (Fin 2) ℂ) : dephase (dephase A) = dephase A := by
  simpa using dephase_idem (ι := Fin 2) (α := ℂ) A

/-- d=2 example: fixed points are diagonal. -/
example (A : Matrix (Fin 2) (Fin 2) ℂ) :
    dephase A = A → ∃ v : Fin 2 → ℂ, A = Matrix.diagonal v := by
  intro h
  exact (dephase_fixed_iff_exists_diagonal (ι := Fin 2) (α := ℂ) A).1 h

end Sbtq
