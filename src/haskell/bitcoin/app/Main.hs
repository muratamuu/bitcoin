module Main where

import Lib
import Ecc

main :: IO ()
main = print $ makeFieldElement 1 2 == makeFieldElement 2 3

