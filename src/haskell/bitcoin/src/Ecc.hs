module Ecc (
  FieldElement,
  makeFieldElement,
  (+),
  (-),
) where

import Prelude hiding ((+), (-))
import qualified Prelude as P

data FieldElement = FieldElement { num :: Int, prime :: Int } deriving (Eq)

instance Show FieldElement where
  show (FieldElement num prime) = "FieldElement_" ++ show num ++ "(" ++ show prime ++ ")"

makeFieldElement :: Int -> Int -> FieldElement
makeFieldElement num prime =
  if (num >= prime || num < 0) then
    error $ "Num " ++ show num ++ " not in field range 0 to " ++ show ((P.-) prime 1)
  else
    FieldElement num prime

(+) :: FieldElement -> FieldElement -> FieldElement
(+) x y =
  if (prime x /= prime y) then
    error $ "Cannot add two numbers in different Fields"
  else
    let num' = ((P.+) (num x) (num y)) `mod` prime x in FieldElement num' (prime x)

(-) :: FieldElement -> FieldElement -> FieldElement
(-) x y =
  if (prime x /= prime y) then
    error $ "Cannot sub two numbers in different Fields"
  else
    let num' = ((P.-) (num x) (num y)) `mod` prime x in FieldElement num' (prime x)

