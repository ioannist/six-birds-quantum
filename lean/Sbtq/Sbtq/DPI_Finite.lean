import Mathlib

open scoped BigOperators

namespace Sbtq

noncomputable section

/-- Deterministic pushforward (coarse-graining). -/
def pushforward {Z X : Type _} [Fintype Z] [Fintype X] [DecidableEq X]
    (f : Z → X) (μ : Z → ℝ) : X → ℝ :=
  fun x => ∑ z : Z, (if f z = x then μ z else 0)

/-- L1 distance on functions. -/
def l1dist {Z : Type _} [Fintype Z] (μ ν : Z → ℝ) : ℝ :=
  ∑ z : Z, |μ z - ν z|

/-- Total variation distance on functions. -/
def tvdist {Z : Type _} [Fintype Z] (μ ν : Z → ℝ) : ℝ :=
  (l1dist μ ν) / 2

lemma sum_indicator_eq {X : Type _} [Fintype X] [DecidableEq X] (a : X) (c : ℝ) :
    (∑ x : X, (if x = a then c else 0)) = c := by
  classical
  simp [Finset.mem_univ]

/-- L1 distance contracts under deterministic pushforward. -/
theorem l1dist_pushforward_le {Z X : Type _} [Fintype Z] [Fintype X] [DecidableEq X]
    (f : Z → X) (μ ν : Z → ℝ) :
    l1dist (pushforward f μ) (pushforward f ν) ≤ l1dist μ ν := by
  classical
  have habs : ∀ x z,
      |(if f z = x then μ z else 0) - (if f z = x then ν z else 0)| =
        (if f z = x then |μ z - ν z| else 0) := by
    intro x z
    by_cases h : f z = x <;> simp [h]

  calc
    l1dist (pushforward f μ) (pushforward f ν)
        = ∑ x : X, |∑ z : Z, ((if f z = x then μ z else 0) - (if f z = x then ν z else 0))| := by
            simp [l1dist, pushforward, Finset.sum_sub_distrib]
    _ ≤ ∑ x : X, ∑ z : Z, |(if f z = x then μ z else 0) - (if f z = x then ν z else 0)| := by
            refine Finset.sum_le_sum ?_
            intro x hx
            have h := (Finset.abs_sum_le_sum_abs
              (f := fun z : Z => (if f z = x then μ z else 0) - (if f z = x then ν z else 0))
              (s := (Finset.univ : Finset Z)))
            simpa using h
    _ = ∑ x : X, ∑ z : Z, (if f z = x then |μ z - ν z| else 0) := by
            simp [habs]
    _ = ∑ z : Z, |μ z - ν z| := by
            have hswap := (Finset.sum_comm (s := (Finset.univ : Finset X)) (t := (Finset.univ : Finset Z))
              (f := fun x z => if f z = x then |μ z - ν z| else 0))
            simpa [sum_indicator_eq] using hswap
    _ = l1dist μ ν := by
            simp [l1dist]

/-- TV distance contracts under deterministic pushforward. -/
theorem tvdist_pushforward_le {Z X : Type _} [Fintype Z] [Fintype X] [DecidableEq X]
    (f : Z → X) (μ ν : Z → ℝ) :
    tvdist (pushforward f μ) (pushforward f ν) ≤ tvdist μ ν := by
  unfold tvdist
  nlinarith [l1dist_pushforward_le (f := f) (μ := μ) (ν := ν)]

-- Concrete finite example
example :
    let Z := Fin 3
    let X := Bool
    let f : Z → Bool := fun z => z.1 = 0
    let μ : Z → ℝ := fun z => if z = 0 then 1 else 0
    let ν : Z → ℝ := fun z => if z = 1 then 1 else 0
    tvdist (pushforward f μ) (pushforward f ν) ≤ tvdist μ ν := by
  intro Z X f μ ν
  simpa using tvdist_pushforward_le (f := f) (μ := μ) (ν := ν)

end

end Sbtq
