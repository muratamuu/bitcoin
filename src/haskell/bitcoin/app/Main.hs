module Main where

import Lib
import Ecc

main :: IO ()
main = print $ FieldElement 1 2 == FieldElement 2 3

