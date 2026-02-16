import Mathlib

namespace Sbtq

/-- Empirical equivalence induced by a family of lenses. -/
def EmpEq {Z ι X : Type _} (f : ι → Z → X) (z z' : Z) : Prop :=
  ∀ i : ι, f i z = f i z'

/-- Setoid of empirical equivalence. -/
def empSetoid {Z ι X : Type _} (f : ι → Z → X) : Setoid Z where
  r := EmpEq f
  iseqv := by
    refine ⟨?refl, ?symm, ?trans⟩
    · intro z i
      rfl
    · intro z z' h i
      symm
      exact h i
    · intro z z' z'' h1 h2 i
      trans f i z'
      · exact h1 i
      · exact h2 i

/-- Leibniz quotient type. -/
def LeibnizQuotient {Z ι X : Type _} (f : ι → Z → X) : Type _ :=
  Quotient (empSetoid f)

/-- Quotient map. -/
def q {Z ι X : Type _} (f : ι → Z → X) : Z → LeibnizQuotient f :=
  Quotient.mk _

/-- Each lens factors through the quotient. -/
def liftLens {Z ι X : Type _} (f : ι → Z → X) (i : ι) : LeibnizQuotient f → X :=
  Quotient.lift (f i) (by
    intro z z' h
    exact h i)

/-- Factorization equation. -/
theorem liftLens_comp_q {Z ι X : Type _} (f : ι → Z → X) (i : ι) (z : Z) :
    liftLens f i (q f z) = f i z :=
  rfl

/-- A map respects empirical equivalence if it is constant on classes. -/
def RespectsEmpEq {Z ι X Y : Type _} (f : ι → Z → X) (g : Z → Y) : Prop :=
  ∀ {z z'}, EmpEq f z z' → g z = g z'

/-- Universal property: maps respecting EmpEq factor uniquely through the quotient. -/
theorem quotient_lift_exists_unique {Z ι X Y : Type _}
    (f : ι → Z → X) (g : Z → Y) (hg : RespectsEmpEq f g) :
    ∃! gbar : LeibnizQuotient f → Y, ∀ z, gbar (q f z) = g z := by
  refine ⟨Quotient.lift g (by
    intro z z' h
    exact hg h), ?spec, ?uniq⟩
  · intro z
    rfl
  · intro gbar hgbar
    funext qz
    refine Quotient.inductionOn qz ?_
    intro z
    calc
      gbar (q f z) = g z := hgbar z
      _ = (Quotient.lift g (by
            intro z z' h
            exact hg h)) (q f z) := by rfl

-- Concrete example with Bool × Bool
example :
    let Z := Bool × Bool
    let ι := Unit
    let X := Bool
    let f : ι → Z → X := fun _ z => z.1
    let g : Z → Bool := fun z => z.1
    ∃ gbar : LeibnizQuotient f → Bool,
      (∀ z, gbar (q f z) = g z) ∧ gbar = liftLens f () := by
  intro Z ι X f g
  have hg : RespectsEmpEq f g := by
    intro z z' h
    exact h ()
  obtain ⟨gbar, hgbar, huniq⟩ := quotient_lift_exists_unique f g hg
  refine ⟨gbar, hgbar, ?_⟩
  have h := huniq (liftLens f ()) (by
    intro z
    rfl)
  exact h.symm

end Sbtq
