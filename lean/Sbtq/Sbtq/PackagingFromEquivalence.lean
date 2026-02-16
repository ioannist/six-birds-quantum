import Mathlib

namespace Sbtq

/-- Saturation of a set under a setoid. -/
def sat {Z : Type _} (s : Setoid Z) (A : Set Z) : Set Z :=
  { z | ∃ a, a ∈ A ∧ s.r z a }

/-- Equivalence class of an element. -/
def classOf {Z : Type _} (s : Setoid Z) (a : Z) : Set Z :=
  { z | s.r z a }

/-- Extensiveness: A ⊆ sat s A. -/
theorem subset_sat {Z : Type _} (s : Setoid Z) (A : Set Z) : A ⊆ sat s A := by
  intro a ha
  rcases s.iseqv with ⟨hrefl, _, _⟩
  exact ⟨a, ha, hrefl a⟩

/-- Monotonicity of saturation. -/
theorem sat_mono {Z : Type _} (s : Setoid Z) {A B : Set Z} : A ⊆ B → sat s A ⊆ sat s B := by
  intro h z hz
  rcases hz with ⟨a, ha, hza⟩
  exact ⟨a, h ha, hza⟩

/-- Idempotence of saturation. -/
theorem sat_idem {Z : Type _} (s : Setoid Z) (A : Set Z) : sat s (sat s A) = sat s A := by
  apply le_antisymm
  · intro z hz
    rcases hz with ⟨a, ha, hza⟩
    rcases ha with ⟨b, hb, hab⟩
    rcases s.iseqv with ⟨_, _, htrans⟩
    exact ⟨b, hb, htrans hza hab⟩
  · exact sat_mono s (subset_sat s A)

/-- A set is a union of equivalence classes if it contains whole classes. -/
def UnionOfClasses {Z : Type _} (s : Setoid Z) (A : Set Z) : Prop :=
  ∀ ⦃a z⦄, a ∈ A → s.r z a → z ∈ A

/-- Fixed points of saturation are exactly unions of classes. -/
theorem sat_eq_iff_unionOfClasses {Z : Type _} (s : Setoid Z) (A : Set Z) :
    sat s A = A ↔ UnionOfClasses s A := by
  constructor
  · intro h a z ha hza
    have : z ∈ sat s A := ⟨a, ha, hza⟩
    simpa [h] using this
  · intro hunion
    apply le_antisymm
    · intro z hz
      rcases hz with ⟨a, ha, hza⟩
      exact hunion ha hza
    · exact subset_sat s A

/-- Saturation as a union of equivalence classes (optional). -/
theorem sat_eq_iUnion_classOf {Z : Type _} (s : Setoid Z) (A : Set Z) :
    sat s A = ⋃ a, ⋃ (_ : a ∈ A), classOf s a := by
  ext z
  constructor
  · intro hz
    rcases hz with ⟨a, ha, hza⟩
    exact (Set.mem_iUnion₂).2 ⟨a, ha, hza⟩
  · intro hz
    rcases (Set.mem_iUnion₂).1 hz with ⟨a, ha, hza⟩
    exact ⟨a, ha, hza⟩

end Sbtq
