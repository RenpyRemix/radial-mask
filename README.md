# Note:
With the new GLSL features of Ren'Py 7.4 and above, this will be easier done through a Shader.  
Should be pretty straight forward math (just test if the target pixel is between the desired angles to the centre). Just the anti-aliasing will need some fine tuning.  
On the #Todo list




# Radial Mask
A Displayable for AlphaMask'ing.  
Pretty straight forward, just set a size, optional center and the start and end degrees

The file starts of with a very basic example using a clockface which you can view by calling the label `radial_mask_example`.  
Please note though that it is not a great example as it uses a timer to tick through the degrees. You'd do better by having a dynamic displayable alter the degree values and return an instance.  
As this is aimed at more experienced programmers, I will leave that to you.

```py
    class RadialMask(renpy.Displayable):
        """                                                                   
        Return an alpha mask for the specified angles radiating 
        from the center. Passed angles are measured in degrees  
        clockwise from the top.

        @kwargs:
            size:    (200,200) - tuple of integer (width, height)
            start:   0.0       - float degree start of shown area
            end:     360.0     - float degree end of shown area

            center:  (*size/2) - tuple of rotation center
        """
```
Pretty much all the information you need to use it.

The keywords, as detailed, create a few attributes to govern the output render:

self.w, self.h :: width and height taken from the size setting  
self.cx, self.cy :: center x and y position taken from the center setting (defaulting to half w, half h)

Those attributes are used to calculate a self.calc_map which basically computes the angle to each corner as well as static values used in the polygon math. Changing any of those values (pretty rare) will result in the calc_map being recomputed.

self.start, self.end :: angle in degrees clockwise from top that the mask starts and ends at

Changing either of these results in a render.invalidate which means the render method is recalled to redraw the displayable. That render method uses the start and end values along with the calc_map to quickly compute the points of a polygon. That polygon is drawn and filled by pygame at a slightly larger size and then downscaled using subpixel_blit to create an anti-aliased version more suitable for masking.

Have fun trying it in your projects and let me know if you find a bug or snaffu.

#### Note:  
If the center is positioned on one of the edges, at or near a corner, angles close to the 90 degree areas might not look the best. They can leave slight gaps between the center and the start of the mask polygon. 


[![Support me on Patreon](https://c5.patreon.com/external/logo/become_a_patron_button.png)](https://www.patreon.com/bePatron?u=19978585)

### Please note:

The way this approach works might not be suitable for complete beginners. It is just a basic displayable to integrate into other code. As such it will likely require a little knowledge of Ren'Py in order to extend it to your particular needs. 

Though I have tried to explain it as simply as possible, I will not be available to help extend it unless under a paid contract.
Basically, if you want it to do more, you are expected to know enough Ren'Py to handle that yourself (or consider paying someone)

### Credits

Clock: https://www.kisscc0.com/free-clock-face/
