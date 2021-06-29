module EccSpec (spec) where

import Test.Hspec
import Ecc

spec :: Spec
spec = do
  describe "add" $
    it "FieldElementの足し算" $
      let a = makeFieldElement 1 2
          b = makeFieldElement 1 2
          c = makeFieldElement 1 2
      in (a + b) `shouldBe` c
