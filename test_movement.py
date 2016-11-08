import unittest
import moviecutter.movement as mcm

class TestMovement(unittest.TestCase):
    def test_linear(self):
        r = mcm.linear((3,5),(5,7),0.5)
        self.assertEqual(r,(4,6))
        self.assertEqual(mcm.linear((3,1),(6,7),1/3),(4,3))

    def test_sinear(self):
        f = mcm.sinFrom((0,5),(5,0),10)
        self.assertEqual(f(0),(0,5))
        self.assertEqual(f(5),(2.5,2.5))
        self.assertEqual(f(10),(5,0))
 
