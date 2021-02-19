import numpy as np
import cv2, PIL
from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
from math import *

camera_parameters_filename = "normal_camera_param.json"
# image_filename = 'markers/snapshot_640_480_17.jpg'
image_filename = '1311/photo_2020-11-13_17-31-59.jpg'

# hsv treshold parameters
upper =  np.array([145, 242, 220])
lower =  np.array([85, 182, 80])

# marker ids
top_left_marker_id = 2 # 3
bottom_right_marker_id = 4 # 11

class ComputerVision:
    def distance(self, p1, p2):
        d = sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
        return d

    def draw_angled_rec(self, x0, y0, width, height, angle, img):
        b = cos(angle) * 0.5
        a = sin(angle) * 0.5
        pt0 = (int(x0 - a * height - b * width), int(y0 + b * height - a * width))
        pt1 = (int(x0 + a * height - b * width), int(y0 - b * height - a * width))
        pt2 = (int(2 * x0 - pt0[0]), int(2 * y0 - pt0[1]))
        pt3 = (int(2 * x0 - pt1[0]), int(2 * y0 - pt1[1]))
        cv2.line(img, pt0, pt1, (255, 255, 255), 3)
        cv2.line(img, pt1, pt2, (255, 255, 255), 3)
        cv2.line(img, pt2, pt3, (255, 255, 255), 3)
        cv2.line(img, pt3, pt0, (255, 255, 255), 3)

    def main(self):
        with open(camera_parameters_filename, "r") as read_file:
            decodedArray = json.load(read_file)
            mtx = np.asarray(decodedArray["mtx"])
            dist = np.asarray(decodedArray["dist"])

        img = cv2.imread(image_filename)
        img = cv2.resize(img, (640, 480))
        h, w = img.shape[:2]

        newCameraMtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
        img = cv2.undistort(img, mtx, dist, None, newCameraMtx)
        raw = img.copy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
        parameters = aruco.DetectorParameters_create()
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        img = aruco.drawDetectedMarkers(img.copy(), corners, ids)

        num = 0
        if ids is not None:
            for i in range(len(ids)):
                c = corners[i][0]
                if ids[i] == top_left_marker_id:
                    center_x1 = c[:, 0].mean()
                    center_y1 = c[:, 1].mean()
                    r1 = self.distance(c[0], c[1])
                    num += 1
                    cv2.circle(img, (c[:, 0].mean(), c[:, 1].mean()), 3, (255, 0, 0), 5)
                if ids[i] == bottom_right_marker_id:
                    center_x2 = c[:, 0].mean()
                    center_y2 = c[:, 1].mean()
                    r2 = self.distance(c[0], c[1])
                    num += 1
                    cv2.circle(img, (c[:, 0].mean(), c[:, 1].mean()), 3, (0, 255, 0), 5)        
        else:
            print("markers not detected")
            cv2.imshow('img', img)
            cv2.waitKey(0)
            return

        if num < 2:
            print("not enough markers detected")
            cv2.imshow('img', img)
            cv2.waitKey(0)
            return

        stand_angle = atan2((center_y2 - center_y1), (center_x2 - center_x1)) - atan2(100, 55)
        # print(stand_angle*180/pi)

        r = (r1 + r2)/2 # average marker size in pixels
        print("r = " + str(r))
        f = 504 # camera focal length in mm 
        height = (20*f/r)/1000 # height from markers to the camera in meters
        pixel_size = f/height

        y_pix = 54.4*pixel_size/1000 # distance from the top-left corner to the first marker
        x_pix = 58*pixel_size/1000
        h_pix = 209*pixel_size/1000 # stand size
        w_pix = 171*pixel_size/1000
        t0_y = h_pix/2 -(29.5/1000)*pixel_size # distance from the top-left corner to the first test tube
        t0_x = w_pix/2 -(30.5/1000)*pixel_size
        d_y = 50*pixel_size/1000 # distance between test tubes
        d_x = 55*pixel_size/1000

        mid = (int((center_x2 + center_x1)/2), int((center_y2 + center_y1)/2)) # stand center
        # cv2.circle(img, mid, 30, (0, 0, 255), 5)
        self.draw_angled_rec(mid[0], mid[1], w_pix, h_pix, stand_angle, img)

        b = cos(stand_angle)
        a = sin(stand_angle)
        initial = (int(mid[0] + a * t0_y - b * t0_x), int(mid[1] - b * t0_y - a * t0_x))
        tubes_coord = {}
        for j in range(4):
            for i in range(3):
                tubes_coord[i+3*j] = (int(initial[0] - a * j * d_y + b * i * d_x), int(initial[1] + b * j * d_y + a * i * d_x))
                cv2.circle(img, tubes_coord[i+3*j], int(15*pixel_size/1000), (0, 0, 255), 2)

        hsv = cv2.cvtColor(raw,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv,lower,upper)
        dilated = cv2.dilate(mask, None, iterations=7)
        # cv2.imshow('mask', dilated)

        _, contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(img, contours, -1, (255, 0, 0), 3)
        cap_r = 17.5/1000 # cap radius in meters
        cap_r *= pixel_size
        cap_area_pix = pi*cap_r**2

        test_tubes = np.zeros((4, 3), dtype=int)
        for cnt in contours:
            if cv2.contourArea(cnt) > 0.5*cap_area_pix:
                cnt = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
                # cv2.drawContours(img, [cnt], -1, (0, 255, 0), 3)
                (x,y),radius = cv2.minEnclosingCircle(cnt)
                center = (int(x),int(y))
                radius = int(radius)
                cv2.circle(img,center,radius,(0,255,0),2)
                d_min = sqrt(w**2+h**2)
                for i in range(12):
                    d = self.distance(tubes_coord[i], center)
                    if d < d_min:
                        d_min = d
                        tube_ind = i
                test_tubes[tube_ind//3][tube_ind%3] = 1

        print(test_tubes)

        y_cam = 57/1000 # distance from third link rotation center to the camera (forward)
        z_cam = 26.5/1000 # distance from third link rotation center to the camera (verticaly)

        plt.figure()
        for i, (x, y) in tubes_coord.items():
            tubes_coord[i] = ((x - w/2)/pixel_size, (h/2 - y)/pixel_size + y_cam)
            plt.plot(tubes_coord[i][0]*1000, tubes_coord[i][1]*1000, "o")
        plt.axis('equal')
        plt.show()
        # print(tubes_coord)

        cv2.imshow('img', img)
        cv2.waitKey(0)

if __name__ == "__main__":
    cv = ComputerVision()
    cv.main()
