import Mathlib

namespace Sbtq

/-- A predicate is definable from f if it factors through f. -/
def DefinableFrom {Z X : Type _} (f : Z → X) (h : Z → Bool) : Prop :=
  ∃ hX : X → Bool, ∀ z, h z = hX (f z)

/-- A predicate is constant on the fibers of f. -/
def ConstantOnFibers {Z X : Type _} (f : Z → X) (h : Z → Bool) : Prop :=
  ∀ ⦃z z'⦄, f z = f z' → h z = h z'

/-- g refines f if f factors through g. -/
def Refines {Z X Y : Type _} (g : Z → Y) (f : Z → X) : Prop :=
  ∃ r : Y → X, ∀ z, f z = r (g z)

/-- Strict refinement: g refines f but not conversely. -/
def StrictlyRefines {Z X Y : Type _} (g : Z → Y) (f : Z → X) : Prop :=
  Refines g f ∧ ¬ Refines f g

/-- Refined lens pairing f with a predicate h. -/
def refinedLens {Z X : Type _} (f : Z → X) (h : Z → Bool) : Z → X × Bool :=
  fun z => (f z, h z)

/-- Definability is equivalent to being constant on fibers. -/
theorem definable_iff_constantOnFibers {Z X : Type _} (f : Z → X) (h : Z → Bool) :
    DefinableFrom f h ↔ ConstantOnFibers f h := by
  constructor
  · intro hdef z z' hz
    rcases hdef with ⟨hX, hh⟩
    calc
      h z = hX (f z) := hh z
      _ = hX (f z') := by simpa [hz]
      _ = h z' := (hh z').symm
  · classical
    intro hconst
    let hX : X → Bool := fun x =>
      if hx : ∃ z, f z = x then h (Classical.choose hx) else false
    refine ⟨hX, ?_⟩
    intro z
    have hx : ∃ z', f z' = f z := ⟨z, rfl⟩
    have hchoose : f (Classical.choose hx) = f z := Classical.choose_spec hx
    have hz : h (Classical.choose hx) = h z := hconst hchoose
    calc
      h z = h (Classical.choose hx) := hz.symm
      _ = hX (f z) := by
        simp [hX, hx]

/-- The refined lens always refines the original lens. -/
theorem refined_refines {Z X : Type _} (f : Z → X) (h : Z → Bool) :
    Refines (refinedLens f h) f := by
  refine ⟨Prod.fst, ?_⟩
  intro z
  rfl

/-- Refines back iff the predicate is definable from f. -/
theorem refines_original_iff_definable {Z X : Type _} (f : Z → X) (h : Z → Bool) :
    Refines f (refinedLens f h) ↔ DefinableFrom f h := by
  constructor
  · intro href
    rcases href with ⟨r, hr⟩
    let hX : X → Bool := fun x => (r x).2
    refine ⟨hX, ?_⟩
    intro z
    have hz : (f z, h z) = r (f z) := hr z
    have hz' : h z = (r (f z)).2 := by
      simpa using congrArg Prod.snd hz
    simpa [hX] using hz'
  · intro hdef
    rcases hdef with ⟨hX, hh⟩
    refine ⟨fun x => (x, hX x), ?_⟩
    intro z
    have : h z = hX (f z) := hh z
    simpa [refinedLens, this]

/-- If h is not definable from f, the refined lens strictly refines f. -/
theorem refined_strictlyRefines_of_notDefinable {Z X : Type _} (f : Z → X) (h : Z → Bool)
    (hn : ¬ DefinableFrom f h) : StrictlyRefines (refinedLens f h) f := by
  refine ⟨refined_refines f h, ?_⟩
  intro href
  have : DefinableFrom f h := (refines_original_iff_definable f h).1 href
  exact hn this

-- Finite counterexample: f sees first bit, h is second bit.
example :
    let Z := Bool × Bool
    let f : Z → Bool := fun z => z.1
    let h : Z → Bool := fun z => z.2
    ¬ DefinableFrom f h := by
  intro Z f h
  intro hdef
  have hconst : ConstantOnFibers f h := (definable_iff_constantOnFibers f h).1 hdef
  have : h (true, false) = h (true, true) := by
    apply hconst
    rfl
  simp [h] at this

end Sbtq
