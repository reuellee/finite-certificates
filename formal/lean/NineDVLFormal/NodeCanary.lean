import NineDVLFormal.GeneratedNodeData

/-!
# 9DVL diagonal-three node-canary formal replay

This module is the first small-kernel formalization checkpoint for the
`DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY` certificate.  It deliberately proves
only the finite semantic layer of the local 17-cell object:

* the declared outer scope boundary is retained and true parent infinity is
  empty;
* the six feasibility profiles induce closed bad subcomplexes;
* the stored integral cellular differentials satisfy `d₁ d₂ = 0`;
* all 216 ordered profile triples have zero middle residue over `F₂` after the
  balanced pair-complex extraction; and
* fail-closed mutations that promote global coverage, invent parent infinity,
  corrupt incidence, or change signature accounting are rejected.

The exact semialgebraic reconstruction of the two affine branches remains
outside this first checkpoint.  A deterministic, independently audited data
bridge ties the finite constants below to the exact JSON certificate bytes.
Consequently this module does not claim global row-2599 coverage or advance
the 2/9 ledger.
-/

namespace NineDVLFormal.NodeCanary

abbrev Simplex := GeneratedNodeData.Simplex
abbrev IntMatrix := GeneratedNodeData.IntMatrix

def chambers : List Simplex :=
  [[0, 1, 2], [0, 2, 3], [0, 3, 4], [0, 1, 4]]

def masterCells : List Simplex := GeneratedNodeData.masterCells

def scopeBoundary : List Simplex := GeneratedNodeData.scopeBoundary

def expectedProfiles : List Nat := GeneratedNodeData.profileCensus.map (·.1)

def expectedProfileCensus : List (Nat × Nat) := GeneratedNodeData.profileCensus

def cellSubset (small large : Simplex) : Bool :=
  small.all fun vertex => large.contains vertex

def faces : Simplex → List Simplex
  | [] => []
  | head :: tail => tail :: (faces tail).map (head :: ·)

def nonemptyFaces (cell : Simplex) : List Simplex :=
  (faces cell).filter fun face => !face.isEmpty

def incidentChambers (cell : Simplex) : List Nat :=
  (List.range chambers.length).filter fun index =>
    cellSubset cell (chambers.getD index [])

def badCells (profile : Nat) : List Simplex :=
  masterCells.filter fun cell =>
    (incidentChambers cell).any fun index => !(profile.testBit index)

def isClosedSubcomplex (cells : List Simplex) : Bool :=
  cells.all fun cell =>
    (nonemptyFaces cell).all fun face => cells.contains face

def allProfileBadSetsClosed (profiles : List Nat) : Bool :=
  profiles.all fun profile => isClosedSubcomplex (badCells profile)

def getInt (matrix : IntMatrix) (row column : Nat) : Int :=
  (matrix.getD row []).getD column 0

def intMatrixColumns (matrix : IntMatrix) : Nat :=
  (matrix.getD 0 []).length

def intMatrixMultiply (left right : IntMatrix) : IntMatrix :=
  (List.range left.length).map fun row =>
    (List.range (intMatrixColumns right)).map fun column =>
      (List.range (intMatrixColumns left)).foldl
        (fun total middle =>
          total + getInt left row middle * getInt right middle column)
        0

def zeroIntMatrix (rows columns : Nat) : IntMatrix :=
  (List.range rows).map fun _ => (List.range columns).map fun _ => 0

def integralD1 : IntMatrix := GeneratedNodeData.integralD1

def integralD2 : IntMatrix := GeneratedNodeData.integralD2

structure F2Matrix where
  nRows : Nat
  nCols : Nat
  rows : List Nat
deriving Repr, BEq

def F2Matrix.row (matrix : F2Matrix) (index : Nat) : Nat :=
  matrix.rows.getD index 0

def isCodimensionOneFace (lower upper : Simplex) : Bool :=
  lower.length + 1 == upper.length && cellSubset lower upper

def incidenceF2 (lower upper : List Simplex) : F2Matrix :=
  { nRows := upper.length
    nCols := lower.length
    rows := upper.map fun high =>
      (List.range lower.length).foldl
        (fun bits column =>
          if isCodimensionOneFace (lower.getD column []) high then
            bits ||| (1 <<< column)
          else bits)
        0 }

def firstSetBit? (row columns : Nat) : Option Nat :=
  (List.range columns).find? fun column => row.testBit column

def reduceRow (columns : Nat) (basis : List Nat) (row : Nat) : Nat :=
  basis.foldl
    (fun value pivotRow =>
      match firstSetBit? pivotRow columns with
      | some pivot => if value.testBit pivot then value ^^^ pivotRow else value
      | none => value)
    row

def insertBasisRow (columns : Nat) (basis : List Nat) (row : Nat) : List Nat :=
  let reduced := reduceRow columns basis row
  if reduced == 0 then basis else basis ++ [reduced]

def rankF2 (matrix : F2Matrix) : Nat :=
  (matrix.rows.foldl (insertBasisRow matrix.nCols) []).length

def multiplyRowF2 (row : Nat) (right : F2Matrix) : Nat :=
  (List.range right.nRows).foldl
    (fun result index =>
      if row.testBit index then result ^^^ right.row index else result)
    0

def productZeroF2 (left right : F2Matrix) : Bool :=
  left.nCols == right.nRows && left.rows.all fun row => multiplyRowF2 row right == 0

def prefixSum (dimensions : List Nat) (index : Nat) : Nat :=
  ((dimensions.take index).foldl (· + ·) 0)

structure MatrixBlock where
  blockRow : Nat
  blockColumn : Nat
  matrix : F2Matrix

def blockMatrix
    (rowDimensions columnDimensions : List Nat)
    (blocks : List MatrixBlock) : F2Matrix :=
  let totalRows := rowDimensions.foldl (· + ·) 0
  let totalColumns := columnDimensions.foldl (· + ·) 0
  { nRows := totalRows
    nCols := totalColumns
    rows := (List.range totalRows).map fun globalRow =>
      blocks.foldl
        (fun result block =>
          let rowOffset := prefixSum rowDimensions block.blockRow
          let columnOffset := prefixSum columnDimensions block.blockColumn
          if rowOffset ≤ globalRow && globalRow < rowOffset + block.matrix.nRows then
            result ||| ((block.matrix.row (globalRow - rowOffset)) <<< columnOffset)
          else result)
        0 }

def intersection (left right : List Simplex) : List Simplex :=
  left.filter fun cell => right.contains cell

def difference (left right : List Simplex) : List Simplex :=
  left.filter fun cell => !(right.contains cell)

def basis (source : List Simplex) (degree : Nat) : List Simplex :=
  masterCells.filter fun cell => cell.length == degree + 1 && source.contains cell

def gradedBasis (source : List Simplex) : List (List Simplex) :=
  [basis source 0, basis source 1, basis source 2]

def basisAt (graded : List (List Simplex)) (degree : Nat) : List Simplex :=
  graded.getD degree []

structure PairExtraction where
  nMatrix : F2Matrix
  mMatrix : F2Matrix

def extractPairComplex (first second third : Nat) : PairExtraction :=
  let bad := [badCells first, badCells second, badCells third]
  let triple := intersection (intersection (bad.getD 0 []) (bad.getD 1 [])) (bad.getD 2 [])
  let exclusive :=
    [difference (intersection (bad.getD 0 []) (bad.getD 1 [])) triple,
     difference (intersection (bad.getD 0 []) (bad.getD 2 [])) triple,
     difference (intersection (bad.getD 1 []) (bad.getD 2 [])) triple]
  let tripleBasis := gradedBasis triple
  let exclusiveBasis := exclusive.map gradedBasis
  let t0 := basisAt tripleBasis 0
  let t1 := basisAt tripleBasis 1
  let t2 := basisAt tripleBasis 2
  let dT0 := incidenceF2 t0 t1
  let dT1 := incidenceF2 t1 t2
  let e0 := exclusiveBasis.getD 0 []
  let e1 := exclusiveBasis.getD 1 []
  let e2 := exclusiveBasis.getD 2 []
  let e00 := basisAt e0 0
  let e01 := basisAt e0 1
  let e02 := basisAt e0 2
  let e10 := basisAt e1 0
  let e11 := basisAt e1 1
  let e12 := basisAt e1 2
  let e20 := basisAt e2 0
  let e21 := basisAt e2 1
  let e22 := basisAt e2 2
  let dE00 := incidenceF2 e00 e01
  let dE01 := incidenceF2 e01 e02
  let dE10 := incidenceF2 e10 e11
  let dE11 := incidenceF2 e11 e12
  let dE20 := incidenceF2 e20 e21
  let dE21 := incidenceF2 e21 e22
  let f00 := incidenceF2 t0 e01
  let f01 := incidenceF2 t1 e02
  let f10 := incidenceF2 t0 e11
  let f11 := incidenceF2 t1 e12
  let f20 := incidenceF2 t0 e21
  let f21 := incidenceF2 t1 e22
  let c0Dimensions := [t0.length, t0.length, e00.length, e10.length, e20.length]
  let c1Dimensions := [t1.length, t1.length, e01.length, e11.length, e21.length]
  let c2Dimensions := [t2.length, t2.length, e02.length, e12.length, e22.length]
  let nMatrix := blockMatrix c1Dimensions c0Dimensions
    [{blockRow := 0, blockColumn := 0, matrix := dT0},
     {blockRow := 1, blockColumn := 1, matrix := dT0},
     {blockRow := 2, blockColumn := 0, matrix := f00},
     {blockRow := 2, blockColumn := 2, matrix := dE00},
     {blockRow := 3, blockColumn := 0, matrix := f10},
     {blockRow := 3, blockColumn := 1, matrix := f10},
     {blockRow := 3, blockColumn := 3, matrix := dE10},
     {blockRow := 4, blockColumn := 1, matrix := f20},
     {blockRow := 4, blockColumn := 4, matrix := dE20}]
  let mMatrix := blockMatrix c2Dimensions c1Dimensions
    [{blockRow := 0, blockColumn := 0, matrix := dT1},
     {blockRow := 1, blockColumn := 1, matrix := dT1},
     {blockRow := 2, blockColumn := 0, matrix := f01},
     {blockRow := 2, blockColumn := 2, matrix := dE01},
     {blockRow := 3, blockColumn := 0, matrix := f11},
     {blockRow := 3, blockColumn := 1, matrix := f11},
     {blockRow := 3, blockColumn := 3, matrix := dE11},
     {blockRow := 4, blockColumn := 1, matrix := f21},
     {blockRow := 4, blockColumn := 4, matrix := dE21}]
  {nMatrix, mMatrix}

structure PairResult where
  middleDimension : Nat
  rankN : Nat
  rankM : Nat
  residue : Nat
deriving Repr, BEq

def pairResult (first second third : Nat) : PairResult :=
  let extraction := extractPairComplex first second third
  let rankN := rankF2 extraction.nMatrix
  let rankM := rankF2 extraction.mMatrix
  let middle := extraction.nMatrix.nRows
  { middleDimension := middle
    rankN
    rankM
    residue := middle - rankN - rankM }

def pairCheck (first second third : Nat) : Bool :=
  let extraction := extractPairComplex first second third
  let result := pairResult first second third
  productZeroF2 extraction.mMatrix extraction.nMatrix && result.residue == 0

def profileTriples (profiles : List Nat) : List (Nat × Nat × Nat) :=
  profiles.flatMap fun first =>
    profiles.flatMap fun second =>
      profiles.map fun third => (first, second, third)

def computedPairResults (profiles : List Nat) : List PairResult :=
  (profileTriples profiles).map fun triple => pairResult triple.1 triple.2.1 triple.2.2

def expectedClosedHistogram : List (PairResult × Nat) :=
  [({middleDimension := 0, rankN := 0, rankM := 0, residue := 0}, 16),
   ({middleDimension := 2, rankN := 2, rankM := 0, residue := 0}, 12),
   ({middleDimension := 3, rankN := 2, rankM := 1, residue := 0}, 24),
   ({middleDimension := 5, rankN := 3, rankM := 2, residue := 0}, 36),
   ({middleDimension := 7, rankN := 5, rankM := 2, residue := 0}, 36),
   ({middleDimension := 8, rankN := 4, rankM := 4, residue := 0}, 3),
   ({middleDimension := 8, rankN := 5, rankM := 3, residue := 0}, 24),
   ({middleDimension := 10, rankN := 6, rankM := 4, residue := 0}, 52),
   ({middleDimension := 13, rankN := 7, rankM := 6, residue := 0}, 12),
   ({middleDimension := 16, rankN := 8, rankM := 8, residue := 0}, 1)]

def histogramMatches (profiles : List Nat) : Bool :=
  let results := computedPairResults profiles
  results.length == 216 &&
    expectedClosedHistogram.all fun expected => results.count expected.1 == expected.2

structure NodeCertificate where
  formatVersion : Nat
  certificateSha256 : String
  parentIndex : Nat
  support : List Nat
  localCoverage : Bool
  globalCoverage : Bool
  scopeBoundary : List Simplex
  parentInfinity : List Simplex
  profileCensus : List (Nat × Nat)
  d1 : IntMatrix
  d2 : IntMatrix
deriving Repr, BEq

def nodeCertificate : NodeCertificate :=
  { formatVersion := GeneratedNodeData.formatVersion
    certificateSha256 := GeneratedNodeData.certificateSha256
    parentIndex := GeneratedNodeData.parentIndex
    support := GeneratedNodeData.support
    localCoverage := GeneratedNodeData.localCoverage
    globalCoverage := GeneratedNodeData.globalCoverage
    scopeBoundary
    parentInfinity := GeneratedNodeData.parentInfinity
    profileCensus := expectedProfileCensus
    d1 := integralD1
    d2 := integralD2 }

def checkNodeCertificate (certificate : NodeCertificate) : Bool :=
  certificate.formatVersion == 1 &&
  certificate.certificateSha256 ==
    "0f387e769568c236c0712f2514f7c28bbcc4fa82a417d6eaa56656976617b2b9" &&
  certificate.parentIndex == 2599 &&
  certificate.support == [15, 15, 15] &&
  certificate.localCoverage &&
  !certificate.globalCoverage &&
  masterCells.length == 17 &&
  certificate.scopeBoundary == scopeBoundary &&
  certificate.parentInfinity.isEmpty &&
  certificate.profileCensus == expectedProfileCensus &&
  (certificate.profileCensus.map (·.2)).foldl (· + ·) 0 == 97224 &&
  allProfileBadSetsClosed (certificate.profileCensus.map (·.1)) &&
  certificate.d1 == integralD1 &&
  certificate.d2 == integralD2 &&
  intMatrixMultiply certificate.d1 certificate.d2 == zeroIntMatrix 5 4 &&
  ((profileTriples (certificate.profileCensus.map (·.1))).all fun triple =>
    pairCheck triple.1 triple.2.1 triple.2.2) &&
  histogramMatches (certificate.profileCensus.map (·.1))

set_option maxHeartbeats 0 in
set_option maxRecDepth 100000 in
theorem nodeCertificateAccepted : checkNodeCertificate nodeCertificate = true := by
  decide

theorem localScopeOnly : nodeCertificate.globalCoverage = false := rfl
theorem trueParentInfinityEmpty : nodeCertificate.parentInfinity = [] := rfl

set_option maxHeartbeats 0 in
set_option maxRecDepth 100000 in
theorem all216ProfileTriplesExact :
    (profileTriples expectedProfiles).all fun triple =>
      pairCheck triple.1 triple.2.1 triple.2.2 = true := by
  decide

def promotedGlobalCoverage : NodeCertificate :=
  {nodeCertificate with globalCoverage := true}

def inventedParentInfinity : NodeCertificate :=
  {nodeCertificate with parentInfinity := [[1], [2], [1, 2]]}

def corruptSignatureAccounting : NodeCertificate :=
  {nodeCertificate with
    profileCensus := [(0, 70967), (3, 72), (6, 72), (9, 72), (12, 72), (15, 25968)]}

def corruptIntegralD2 : IntMatrix :=
  [[-1,  0,  0, -1],
   [-1,  1,  0,  0],
   [ 0, -1,  1,  0],
   [ 0,  0, -1,  1],
   [ 1,  0,  0,  0],
   [ 0,  1,  0,  0],
   [ 0,  0,  1,  0],
   [ 0,  0,  0,  1]]

def corruptIncidence : NodeCertificate :=
  {nodeCertificate with d2 := corruptIntegralD2}

set_option maxHeartbeats 0 in
set_option maxRecDepth 100000 in
theorem hostileMutationsRejected :
    checkNodeCertificate promotedGlobalCoverage = false ∧
    checkNodeCertificate inventedParentInfinity = false ∧
    checkNodeCertificate corruptSignatureAccounting = false ∧
    checkNodeCertificate corruptIncidence = false := by
  decide

#print axioms nodeCertificateAccepted
#print axioms all216ProfileTriplesExact
#print axioms hostileMutationsRejected

end NineDVLFormal.NodeCanary
