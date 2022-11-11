# RBE549: Building Built in Minutes using SfM
# Karter Krueger and Tript Sharma
# Wrapper.py

import argparse
import numpy as np
import cv2
import os
from ParseData import *
from GetInliersRANSAC import getInliersRANSAC
from EstimateFundamentalMatrix import plotEpipolarLines
import Utils
from EssentialMatrixFromFundamentalMatrix import *
from ExtractCameraPose import *
from DisambiguateCameraPose import *
from NonlinearTriangulation import *

argparser = argparse.ArgumentParser()
argparser.add_argument('--matches_folder_path', default=DEFAULT_MATCHES_FOLDER)
argparser.add_argument('--calib_file_path', default=DEFAULT_CALIBRATION_FILENAME)
args = argparser.parse_args()

K = K_matrix(args.calib_file_path)
correspondences = parse_matches(file_number=1,folder_path=args.matches_folder_path)

img1 = cv2.imread(os.path.join(os.getcwd(),'Phase1/Data/P3Data/1.png'))
img2 = cv2.imread(os.path.join(os.getcwd(),'Phase1/Data/P3Data/2.png'))

F, inlier_set  = getInliersRANSAC(correspondences['12'], eps=0.02, n_iterations=100, K=K)
print(F)
# show_feature_matches(img1,img2,correspondences['12'][inlier_set,:])
F_cv, mask = cv2.findFundamentalMat(correspondences['12'][inlier_set,3:5],correspondences['12'][inlier_set,5:7],cv2.FM_LMEDS)
print(F_cv)
# Utils.verifyWithOpenCV(F,correspondences['12'][inlier_set,3:5],correspondences['12'][inlier_set,5:7], img1 , img2)

E = essentialMatrixFromFundamentalMatrix(F,K)
candidate_pose_list = CamPoseFromE(E)
X, pose, candidate_X, inlier_count = disambiguateCamPoseAndTriangulate([correspondences['12'][inlier_set,3:5],correspondences['12'][inlier_set,5:7]],candidate_pose_list,K)
# print(X)

# Utils.plotTriangulation(X[:,0],X[:,2])
# Utils.plotAllTriangulation(candidate_X)
# Utils.plotTriangulation(X[:,0],X[:,1],X[:,2])
# fig.show()

C1 = np.zeros(3)
R1 = np.eye(3)
C2 = candidate_pose_list[0][0]
R2 = candidate_pose_list[0][1]
I = np.eye(3)
P1 = K @ R1 @ np.hstack((I, -C1.reshape((-1,1))))
P2 = K @ R2 @ np.hstack((I, -C2.reshape((-1,1))))
X_optimized = nonLinearTriangulation(X,P1,P2,correspondences['12'][inlier_set,3:5],correspondences['12'][inlier_set,5:7])

# fig = Utils.plotTriangulation(X_optimized[:,0],X_optimized[:,2])

Utils.plotTriangulationResults((P1@X.T).T, (P1@X_optimized.T).T, correspondences['12'][inlier_set,3:5], img1.copy())