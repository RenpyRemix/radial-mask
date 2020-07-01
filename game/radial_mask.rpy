## To view example in your game add
##
##  call radial_mask_example
##
## somewhere in your running label script



            ###########################################
            #                                         #
            #           To use in your game           #
            #                                         #
            #   Just use it as you would any other    #
            #   displayable object. Note you can      #
            #   alter the attributes after creation   #
            #   and it will recalculate what to show  #
            #                                         #
            ###########################################


### Horrible example usage. Using screen timer to adjust it is 
### not really the optimum approach.


image clockface = "images/kisscc0-clockface.png"

default clockmask = RadialMask(size=(300,300))

default end_degrees = 360.0

screen clockcountdown():

    add AlphaMask("clockface", clockmask) at truecenter

    timer 0.02:
        repeat True 
        # when it hits 0.0 it gets reset to 360.0
        action SetField(clockmask, "end", clockmask.end - 1.0)

label radial_mask_example:

    scene expression "#AAA"

    "Radial Mask clockface ..."

    show screen clockcountdown

    "..."

    hide screen clockcountdown

    return



        ###################################################
        #                   Radial Mask                   #
        ###################################################

init python:

    import math
    from renpy.display.render import render, Render, Matrix2D
    
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
        def __init__(self, **kwargs):
            # this also creates self.w and self.h
            self.size = kwargs.pop('size', (200, 200))

            self.center = kwargs.pop('center', (self.w / 2.0, self.h / 2.0))

            self.start = kwargs.pop('start', 0.0)
            self.end = kwargs.pop('end', 360.0)

            # To give an anti-alias to the angled edges, we create the 
            # render this much larger then downscale it. This value could
            # be altered if a certain mask looks jagged
            self.aascale = kwargs.pop('aascale', 1.129)

            self.build_calc_map()

            super(RadialMask, self).__init__(**kwargs)


        def __setattr__(self, attr, value):

            if attr in ["start", "end"]:

                value = float(value)

                if value not in [0.0, 360.0]:

                    value %= 360.0

                self.__dict__[attr] = value

                renpy.display.render.invalidate(self)

            elif attr in ["size", "center"]:

                self.__dict__["w" if attr == "size" else "cx"] = value[0]
                self.__dict__["h" if attr == "size" else "cy"] = value[1]
                self.__dict__["calcs_are_dirty"] = True

                renpy.display.render.invalidate(self)

            else:

                if attr in ["w", "h", "cx", "cy"]:

                    self.__dict__["calcs_are_dirty"] = True

                    renpy.display.render.invalidate(self)

                super(RadialMask, self).__setattr__(attr, value)


        def build_calc_map(self):
            """
            Just setup some values based on the size and center

            Size and Center should not often change so it makes 
            sense to calculate and store these values once
            """
            self.cxe, self.cye = self.w - self.cx, self.h - self.cy

            # Each element includes corner info and values to calculate
            # positions along the side prior to reaching that corner
            #
            # [
            # Angle to corner 
            # corner x,y
            # adjacent length
            # index to calculate (other is corner value)
            # mid angle ratio
            # dir (1 or -1 - after lower right we invert the added length)
            # ]
            self.calc_map = [
                # Top Right, Base Right, Base Left, Top Left
                [None, [float(self.w),0.0], self.cy, 0, 0.0, -1],
                [None, [float(self.w),float(self.h)], self.cxe, 1, 90.0, -1], 
                [None, [0.0,float(self.h)], self.cye, 0, 180.0, 1], 
                [None, [0.0,0.0], self.cx, 1, 270.0, 1]] 

            # Now determine those angles 
            # First checking if the centre is along any edge
            if not self.cy:
                # centre is on top edge
                if not self.cx:
                    # centre is top left
                    self.calc_map[0][0] = 90.0 #[-180.0, 90.0]
                    self.calc_map[2][0] = 180.0 #[-180.0, 90.0]
                    self.calc_map[3][0] = 315.0 #[-1.0, -1.0]
                elif not self.cxe:
                    # centre is top right
                    self.calc_map[0][0] = 45.0 #[-1.0, -1.0]
                    self.calc_map[1][0] = 180.0 #[-90.0, 180.0]
                    self.calc_map[3][0] = 270.0 #[-90.0, 180.0]
                else:
                    # somewhere along top
                    self.calc_map[0][0] = 90.0 #[-1.0, 90.0]
                    self.calc_map[3][0] = 270.0 #[270.0, -1.0]

            elif not self.cye:
                # centre on lower edge
                if not self.cx:
                    # centre is lower left
                    self.calc_map[1][0] = 90.0 #[90.0, -1.0]
                    self.calc_map[2][0] = 225.0 #[-1.0, -1.0]
                    self.calc_map[3][0] = 360.0 #[-1.0, 0.0]........................
                elif not self.cxe:
                    # centre is lower right
                    self.calc_map[0][0] = 0.0 #[0.0, -1.0]
                    self.calc_map[1][0] = 135.0 #[-1.0, -1.0]
                    self.calc_map[2][0] = 270.0 #[-1.0, 270.0]
                else:
                    # somewhere along lower edge
                    self.calc_map[1][0] = 90.0 #[90.0, -1.0]
                    self.calc_map[2][0] = 270.0 #[-1.0, 270.0]

            elif not self.cx:
                # somewhere along left edge
                self.calc_map[2][0] = 180.0 #[180.0, -1.0]
                self.calc_map[3][0] = 360.0 #[-1.0, 0.0]

            elif not self.cxe:
                # somewhere along right edge
                self.calc_map[0][0] = 0.0 #[0.0, -1.0]
                self.calc_map[1][0] = 180.0 #[-1.0, 180.0]

            if self.calc_map[0][0] is None:
                self.calc_map[0][0] = math.degrees(
                        math.atan(float(self.cxe) / self.cy))

            if self.calc_map[1][0] is None:
                self.calc_map[1][0] = 180.0 - math.degrees(
                        math.atan(float(self.cxe) / self.cye))

            if self.calc_map[2][0] is None:
                self.calc_map[2][0] = 180.0 + math.degrees(
                        math.atan(float(self.cx) / self.cye))

            if self.calc_map[3][0] is None:
                self.calc_map[3][0] = 360.0 - math.degrees(
                        math.atan(float(self.cx) / self.cy))

            # print("Calc Map: {}".format(self.calc_map))

            self.calcs_are_dirty = False
            


        def get_edge_point(self, angle=0.0):
            ## Return the (x,y) coords where angle exits the box
            if angle > 360.0:
                angle %= 360.0

            ## We ignore any angle not pointing through the rect
            if (    (not self.cx and 180.0 < angle < 360.0)
                    or 
                    (not self.cxe and angle < 180.0)
                    or
                    (not self.cy and (angle > 270.0 or angle < 90.0))
                    or
                    (not self.cye and (90.0 < angle < 270.0))):

                return None

            calc_map = self.calc_map[0]

            for k in range(4):
                
                if angle <= self.calc_map[k][0]:

                    calc_map = self.calc_map[k]
                    break

            calc_pos = calc_map[1][:]

            calc_angle = math.radians((calc_map[4] - angle) % 360.0)

            calc_pos[calc_map[3]] = (
                [self.cx,self.cy][calc_map[3]] 
                + (calc_map[5] ### 1 or -1
                    * (calc_map[2] * math.tan(calc_angle))))

            return [float(calc_pos[0]), float(calc_pos[1])]


        def get_polygon_points(self):
            # Return a list of [x,y] points making the polygon

            end_c = self.end + (0.0 if self.end >= self.start else 360.0)

            pointlist = [(self.cx, self.cy)]

            edge_start = self.get_edge_point(self.start)

            if edge_start:

                pointlist.append(edge_start)

            past_start, before_end = [], []

            for k in range(4):

                angle, corner = self.calc_map[k][:2]

                if end_c >= angle >= self.start:

                    past_start.append(corner)

                if angle + 360.0 <= end_c:

                    before_end.append(corner)

            pointlist.extend(past_start)
            pointlist.extend(before_end)

            edge_end = self.get_edge_point(self.end)

            if edge_end:

                pointlist.append(edge_end)

            pointlist.append((self.cx, self.cy))

            ## There are a few settings that do not render as we might
            ## expect. Test for them and adjust
            #
            # Y > 0, X = 0, (end = 0.0 or 360.0 or start == 180.0) bad
            if not self.cx and self.cy:

                if not self.end % 360.0 and self.start:

                    pointlist = [k for k in pointlist if k != [0.0,0.0]]

                if self.start == 180.0:

                    pointlist = [
                        k for k in pointlist if k != [0.0,float(self.h)]]

            # print("After: {} to {}: {}".format(
            #     self.start, end_c, pointlist))

            return pointlist


        def render(self, width, height, st, at):

            if self.calcs_are_dirty:
                # Changed size or center, so recalculate some values
                self.build_calc_map()

            if self.start == self.end or self.end + 360.0 == self.start:

                return renpy.Render(self.w, self.h)

            render = renpy.Render(
                self.w * self.aascale, self.h * self.aascale)
            canvas = render.canvas()

            pointlist = self.get_polygon_points()

            pointlist = [
                (k[0] * self.aascale, k[1] * self.aascale) for k in pointlist]

            canvas.polygon(
                renpy.easy.color("#FFF"), 
                pointlist)

            newcr = Render(self.w, self.h)
            bwr = 1.0 / self.aascale
            newcr.reverse = Matrix2D(bwr, 0, 0, bwr)
            newcr.forward = Matrix2D(self.aascale, 0, 0, self.aascale)
            newcr.subpixel_blit(render, (0, 0))

            return newcr


        def visit(self):
            # We draw our render from data, so have nothing to predict
            return []

