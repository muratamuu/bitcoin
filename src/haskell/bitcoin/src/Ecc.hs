module Ecc where

data FieldElement = FieldElement Int Int deriving (Eq)

instance Show FieldElement where
  show (FieldElement num prime) = "FieldElement_" ++ show num ++ "(" ++ show prime ++ ")"

makeFieldElement :: Int -> Int -> FieldElement
makeFieldElement num prime =
  if (num >= prime || num < 0) then
    error $ "Num " ++ show num ++ " not in field range 0 to " ++ show (prime - 1)
  else
    FieldElement num prime
