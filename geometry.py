""" 
Module implementing the basic geometry features of points and segments.
Defining relative minimal distances and directions.

Requirements
------------
Package numpy which can be installed via PIP.
Python 3.9 or higher.

Notes
-----
This module is provided as material for the phase 2 project for DM857, DS830 (2024). 
"""
from __future__ import annotations
import numpy as np
from abc import ABC,abstractmethod

class shape(ABC):
    """ generic shape class """
    def __init__(self , points : list[tuple[int]]):
        self.pts = points
    
    def __eq__(self , shape):
        assert type(self) is type(shape)
        return self.pts == shape.pts
        
    @abstractmethod
    def min_distance(self,ashape:shape):
        raise NotImplementedError()

    @abstractmethod
    def get_pt(self,idx:int=0):
        raise NotImplementedError()


    def shortest_path(self,ashape:shape):
        raise NotImplementedError()
    
class point(shape):
    """
    Point type defined by a list of one tuple of coordinates
    """

    def __init__(self , points : list[tuple[int]]):
        """
        Construct the point type
        """
        assert isinstance(points,list) and len(points)==1 
        super().__init__(points)
    
    def __str__(self):
        return f"point: {self.pts[0][0]} {self.pts[0][1]}"
    
    def get_pt(self,idx:int=0):
        assert idx==0
        return self

    def get_x(self,idx:int=0):
        assert idx==0
        return self.pts[0][0]

    def get_y(self,idx:int=0):
        assert idx==0
        return self.pts[0][1]

   
    def shortest_path(self,ashape:shape)->tuple:
        """
        Returns the minimal relative vector connecting the two shapes
        >>> p = point([(2,4)])
        >>> s = segment([(-20,3),(40,3)])
        >>> p.shortest_path(s) == (0.0, -1.0)
        True
        """
        if isinstance(ashape,segment):
            a = np.array(ashape.pts[0])
            b = np.array(ashape.pts[1])
            c = np.array([[0,-1],[1,0]]) @ (b-a)
            c = c / np.sqrt(c @ c)
            p = np.array(self.pts[0])
            lval = (p-a) @ (b-a) /((b-a) @ (b-a) )
            if (lval >=0  ) and (lval <=1  ):
                return tuple((((a-p) @ c )* c ).tolist())
            else:
                if( (a-p)@ (a-p) < (b-p)@ (b-p)):
                    return tuple((a-p).tolist())
                else:
                    return tuple((b-p).tolist())
        elif isinstance(ashape,point):
            a = np.array(ashape.pts[0])
            p = np.array(self.pts[0])
            return tuple((a-p).tolist())
        else:
            raise Exception("unknown shape")
    
    def min_distance(self,shape):
        """
        Returns the minimal distance separting the two shapes
        >>> p = point([(2,4)])
        >>> s = segment([(-20,3),(40,3)])
        >>> p.min_distance(s)
        1.0
        >>> p2 = point([(22,4)])
        >>> p.min_distance(p2)
        20.0
        """
        a = np.array(self.shortest_path(shape))
        return (np.sqrt(a@a)).astype(float)
        
    def first_along(self, dx:float, direction:tuple, points:list[point])->point:
        """
        return the closest point along the direction "direction" with maximal distance dx
        >>> s = segment([(2,3),(2.8547875152217292,6.9076000695850475)])
        >>> c = s.direction
        >>> p = point([(2,3)])
        >>> points = [point([(2.4273937576108646,4.953800034792524)]),point([(2.6410906364162967,5.930700052188785)]),point([(2.2,3)]),point([(1.7863031211945677,2.023099982603738)])]
        >>> p.first_along(2.5,c,points) == point([(2.4273937576108646,4.953800034792524)])
        True
        >>> p.first_along(1.5,c,points) == point([(2.3205453182081484,4.465350026094392)])
        True
        >>> p.first_along(0.1,c,points) == point([(2.021369687880543,3.0976900017396263)])
        True
        >>> p.first_along(0.0,c,points) == p
        True
        >>> points[0].first_along(3.0,c,points) == points[0]
        True
        """
        dir = np.array(direction)
        assert np.isclose(1. , np.linalg.norm(dir))
        seq = []
        p0 = np.array(self.pts[0])
        for pl in points:
            p2 = np.array(pl.pts[0])
            det = (p2[0] -p0[0])*dir[1] - (p2[1] - p0[1])*dir[0]
            if np.isclose(det,0.):
                l = (p2-p0) @ dir
                if l>=0 :
                    seq.append(l)
        seq.append(dx)
        l = min(seq)
        
        return point([tuple((p0 + l * dir ))])
    
class segment(shape):
    """
    Segment type defined by a list of two tuple of coordinates
    """
    def __init__(self , points : list[tuple[int]]):
        """
        Construct the segment type and evaluate the associate direction vector.
        The direction vector has norm=1.
        
        >>> s = segment([(-20,3),(40,3)])
        >>> s.direction 
        (1.0, 0.0)
        """
        assert isinstance(points,list) and len(points)==2
        super().__init__(points)
        self.direction = (np.array(self.pts[1]) - np.array(self.pts[0])) 
        self.direction = tuple((self.direction / np.sqrt(self.direction @ self.direction)).tolist())

    def __str__(self):
        return f"segment: {self.pts[0][0]} {self.pts[0][1]} -> {self.pts[1][0]} {self.pts[1][1]}"

    def get_pt(self,idx):
        assert idx < 2
        return point([self.pts[idx]])

    def min_distance(self,ashape:point):
        """
        Evaluate the minimal distance of the segment from a generic point
        >>> p = point([(2,4)])
        >>> s = segment([(-20,3),(40,3)])
        >>> s.min_distance(p)
        1.0
        """
        assert isinstance(ashape,point)
        return ashape.min_distance(self)
    
  

if __name__ == "__main__": 
    from doctest import testmod 
    testmod()
