'''
Created on 2016. 10. 5.

@author: Sungho Lee
@version: 2015/09/16
@note: Convert Bruker raw '2dseq' to Nifti formated image

'''

import re  # Regular Expression
import os
import sys
import logging
from operator import truediv
# from blaze.partition import slices1d
from pjo.dao.SourceDao import SourceDao
from pjo.util.PjoUtil import CommonUtil

logger = logging.getLogger("devLog")
errLogger = logging.getLogger("errLog")


try:
    import nibabel as nib
    import numpy as np
    import json
except:
    errLogger.error("Required libraries (numpy, nibabel, json) are not installed")
    sys.exit(0)


class Brk2nii(object):

    #==============================================================================
    #  Constructor
    #==============================================================================
    def __init__(self):
        pass

    
    
    #==============================================================================
    #  Derive
    #==============================================================================
    def derive(self, title, fileDict, scanObj):


        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          1. Set Path
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        source_path = CommonUtil().f_getPath("S")

        subject_path = title
        sPath = os.path.join(source_path, subject_path, scanObj.scan_num)
        pid = scanObj.pid
        logger.debug("Source Path==[" + sPath + "] PID==[" + pid + "]")


        mtd_path = os.path.join(sPath,'method')
        img_path = os.path.join(sPath, 'pdata', pid, '2dseq')
        reco_path = os.path.join(sPath, 'pdata', pid, 'reco')


        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          2. Set Dictionary
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        param_dict = dict()

        try:
            with open(mtd_path, 'r') as mtdfile:
                for line in mtdfile:
    
                    if re.search(r'^\#\#\$.*=.*', line):
                        splitted = re.split(r'\=', line.strip())
    
                        key = re.sub(r'^\#\#\$(.*)', r'\1', splitted[0])
                        value = splitted[1].strip()
                        if re.search(r'\(\s\d{1,}\s\)', value):
                            nvalue = re.sub(r'\(\s(\d{1,})\s\)', r'\1', value)
    
                            if int(nvalue) > 1:
                                value = next(mtdfile).strip().split()
                                try:
                                    value = map(int, value)
                                except:
                                    try:
                                        value = map(float, value)
                                    except:
                                        pass
                            else:
                                value = next(mtdfile).strip()
    
                        try:
                            value = int(value)
                        except:
                            try:
                                value = float(value)
                            except:
                                pass
    
                        param_dict[key] = value
                    else:
                        pass
        except Exception, e:
            errLogger.error(e)

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          3. Check
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        # Check reconstruction has been processed or not
        if pid > 1:
            
            try:
                with open(reco_path, 'r') as rcofile:
                    reco_param = r'.*RECO_size=(.*)'
                    for line in rcofile:
                        if re.search(reco_param, line):
                            
                            # Fov(cm) * 10(change cm to mm) = Matrix * resolution 
                            recoMatrix = map(int, re.sub(reco_param, r'\1', next(rcofile)).strip().split())
                            fov = param_dict['PVM_FovCm']
                            fov = map(lambda x:x*10, fov)
                            recoReso = map(truediv, fov, recoMatrix)
                            
                            param_dict['Matrix'] = recoMatrix
                            param_dict['RECO'] = True
                            param_dict['Resolution'] = recoReso
                            
            except Exception, e:
                errLogger.error(e)
                pass
        else:
            param_dict['Matrix'] = param_dict['PVM_Matrix']
            param_dict['Resolution'] = param_dict['PVM_SpatResol']


        # Check Datatype - Need to be update if Bruker provide more set of dtype
        try:
            dt = np.dtype('uint16')
            if 'RECO_wordtype' in param_dict.keys():
                if param_dict['RECO_wordtype'] == '_32BIT_SGN_INT':
                    dt = np.dtype('uint32')
    
    
            # Check Temporal Dimension and resolution
            frames = param_dict['PVM_NRepetitions']
            if 'NSegments' in param_dict.keys():
                tr = param_dict['PVM_RepetitionTime'] * param_dict['NSegments'] * param_dict['PVM_NAverages']
            else:
                tr = param_dict['PVM_RepetitionTime'] * param_dict['PVM_NAverages']
    
            if frames == 1:
                dim = []
            else:
                dim = [frames]
        except Exception, e:
            errLogger.error(e)



        # Check Spatial Dimention, resolution and orientation
        #   - 'L_R'     left to right            (x axis of gradient coil)
        #   - 'A_P'     anterior to posterior    (y axis of gradient coil)
        #   - 'H_F'     head to foot             (z axis of gradient coil)
        corrcoef = {'L_R': [-1, 0], 'A_P': [-1, 2], 'H_F': [1, 1]}
        ori_dict = {'axial': ['L_R', 'A_P'],
                    'coronal': ['L_R', 'H_F'],
                    'sagittal': ['A_P', 'H_F']}
        rdout_ori = param_dict['PVM_SPackArrReadOrient']
        slice_ori = param_dict['PVM_SPackArrSliceOrient']
        matrix = param_dict['Matrix']
        slices = param_dict['PVM_SPackArrNSlices']
        resol = param_dict['Resolution']

        logger.debug("rdout_ori=[%s]", rdout_ori)
        logger.debug("slice_ori=[%s]", slice_ori)
        logger.debug("matrix=[%s]", matrix)
        logger.debug("slices=[%s]", slices)
        logger.debug("resol=[%s]", resol)


        if type(slice_ori) == list:
            errLogger.error('Can not derive this file. ')
            raise Exception('Can not derive this file. ')

        try:
            axis_order = ori_dict[slice_ori][:]
            
            axis_order.extend([ori for ori in corrcoef.keys() if ori not in axis_order])
            redirect = [corrcoef[axis][0] for axis in axis_order]
    
            # coronal view has oposite direction, need to check sagittal view later
            if slice_ori == 'coronal':
                redirect = list(-np.array(redirect))
            redirect.append(1)
            reori = [corrcoef[axis][1] for axis in axis_order]
            reori.append(3)
            logger.debug("redirect=[%s]", redirect)
            logger.debug("reori=[%s]", reori)
    
    
            if param_dict['PVM_SpatDimEnum'] == '2D':
                matrix.append(slices)
                resol.append(param_dict['PVM_SPackArrSliceDistance'])
                matrix = matrix[::-1]
            elif param_dict['PVM_SpatDimEnum'] == '3D':
                matrix = np.roll(matrix, 1)
                resol = np.roll(resol, 1)[::-1]
            else:
                dim = [len(slice_ori)]
            dim.extend(matrix)
    
            logger.debug("matrix=[%s]", matrix)
            logger.debug("resol=[%s]", resol)
            logger.debug("dim=[%s]", dim)
        except Exception, e:
            errLogger.error(e)
            
            

        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          4. Get/Set File Name Info
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

        # Make .json file - BIDS standard need to be integrated
        fileName = CommonUtil().f_getFileName(fileDict, scanObj)
        logger.debug("FileName ===> [" + fileName + "]")
                
        
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          5. Make Path
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        dPath = CommonUtil().f_getFolderName(fileDict, scanObj.meta_data_type)
        logger.debug("Derivative Path ===> [" + dPath + "]")
        
        if not os.path.isdir(dPath):
            os.makedirs(dPath)

        
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          6-1. Make JSON File
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        try:
            with open(os.path.join(dPath, '%s.json' % fileName), 'w') as fp:
                logger.debug("Create Json==")
                json.dump(param_dict, fp, ensure_ascii=False)
        except Exception, e:
            errLogger.error(e)


        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          6-2. Make Image File
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        try:
            # Print out the result image dimension and resolution
            shape = param_dict['Matrix']
            logger.debug("shape ===> [ %s ]", shape)
            
            if len(shape) == 3:
                shape.append(frames)
            else:
                shape.append(slices)
                shape.append(frames)
            logger.debug("Image dimension: %d, Image shape: %s" % (len(shape), str(shape)))
        except Exception, e:
            errLogger.error(e)
            
            
        # Import image binary from Bruker raw
        try:
            img = np.transpose(np.fromfile(img_path, dtype=dt).reshape(dim))
        except BaseException("Unmatch matrix size!") as e:
            errLogger.error(e)
            sys.exit(0)
        except Exception, e:
            errLogger.error(e)

        # Integrate header information from parameters
        img_affn = nib.affines.from_matvec(np.diag(resol), np.zeros(3))
        img_nii = nib.Nifti1Image(img, img_affn)
#         affine = img_nii.header.get_base_affine()
#         logger.debug("img affine====") 
               
        # SliceOrder - need to be modified if different case is exist
        # img_nii.header['intent_code'] need to be added if DTI image is performed
        if param_dict['PVM_ObjOrderScheme'] == 'Interlaced':
            slice_code = 3
        else:
            slice_code = 0
        
        
        try:
            # img_nii.header['freq_dim'], img_nii.header['slice_dim'], img_nii.header['phase_dim'] need to be added
            #   if spiral scan is performed
            # img_nii.header['slice_start'], img_nii.header['slice_end'] need to be added if slice padding is performed
            if len(dim) == 4:
                img_nii.header.set_xyzt_units('mm', 'sec')
                img_nii.header['pixdim'][4] = float(tr)/1000
                img_nii.header['slice_duration'] = float(tr)/(1000 * slices)
                img_nii.header['slice_code'] = slice_code
            else:
                img_nii.header.set_xyzt_units('mm')
    
            img_nii.header['sform_code'] = 0
            img_nii.header['qform_code'] = 1
        
            # Apply qform affine matrix
            qform = np.diag(img_affn) * redirect
            i = np.argsort(reori)
            img_nii.set_qform(np.diag(qform)[i, :])
#             logger.debug("Apply qform ====")
    
            # Save to NifTi file
            fileName = fileName + ".nii.gz"
            img_nii.to_filename(os.path.join(dPath, fileName))
            img_nii.to_file_map()
#             logger.debug("Save nii file ====")
            
        except Exception, e:
            errLogger.error(e)


        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
          6. UPDATE DB - SCAN
        '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
        if os.path.isfile(os.path.join(dPath, fileName)):
            sDao = SourceDao()
            sDao.updateScanDeriveYn(scanObj.id)
            return True
        else: 
            raise Exception('Can not make this file. ')
            return False

        
        


    #==============================================================================
    #  Get Json File Info
    #==============================================================================
    def getJsonFileInfo(self, folderName, fileName):

        try:
            with open(os.path.join(folderName, fileName), 'r') as jsonfile:
                for line in jsonfile:
                    jsonObj = json.loads(line)
        except Exception, e:
            errLogger.error(e)

        # Return Dictionary
        dicJson = {}
        
        try:
            dicJson['Method'] = jsonObj['Method']
            dicJson['dtype'] = jsonObj['RECO_wordtype']
    
            dicJson['SpatResol'] = jsonObj['Resolution']
            dicJson['SliceThick'] = jsonObj['PVM_SliceThick']
            dicJson['SliceGap'] = jsonObj['PVM_SPackArrSliceGap']
            dicJson['SliceDistance'] = jsonObj['PVM_SPackArrSliceDistance']
            dicJson['Matrix'] = jsonObj['Matrix']
            dicJson['NSlices'] = jsonObj['PVM_SPackArrNSlices']
            dicJson['Repetitions'] = jsonObj['PVM_NRepetitions']
            dicJson['SliceOrient'] = jsonObj['PVM_SPackArrSliceOrient']
            dicJson['ReadOrient'] = jsonObj['PVM_SPackArrReadOrient']
            dicJson['NSegments'] = jsonObj['NSegments']
            dicJson['RepetitionTime'] = jsonObj['PVM_RepetitionTime']
            dicJson['NAverages'] = jsonObj['PVM_NAverages']
            dicJson['OrderScheme'] = jsonObj['PVM_ObjOrderScheme']
            dicJson['Dim'] = jsonObj['PVM_SpatDimEnum']
        except Exception, e:
            errLogger.error(e)
            
        return dicJson




   
