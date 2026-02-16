import Mathlib

namespace Sbtq

abbrev Z := Fin 4

namespace Function
/-- Idempotent endomap. -/
def Idempotent {α : Type _} (f : α → α) : Prop := ∀ x, f (f x) = f x
end Function

/-- Projection onto {0,1}. -/
def E : Z → Z := fun x => if x = 0 then 0 else 1

/-- Projection onto {0,2} via threshold on the underlying Nat. -/
def F : Z → Z := fun x => if x.1 < 2 then 0 else 2

/-- E is idempotent. -/
theorem E_idem : Function.Idempotent E := by
  intro x
  fin_cases x <;> simp [E]

/-- F is idempotent. -/
theorem F_idem : Function.Idempotent F := by
  intro x
  fin_cases x <;> simp [F]

/-- E and F do not commute. -/
theorem not_commute_E_F : ¬ Function.Commute E F := by
  intro h
  have h2 : (1 : Fin 4) = 0 := by
    have h' := h (2 : Fin 4)
    simpa [E, F] using h'
  have : (1 : Fin 4) ≠ 0 := by decide
  exact this h2

/-- Explicit mismatch witness. -/
theorem mismatch_witness : E (F (2 : Fin 4)) ≠ F (E (2 : Fin 4)) := by
  decide

end Sbtq
