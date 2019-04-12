# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 17:27:42 2019

@author: Juen
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

from gbp_video_module import denormalize_buffer

def plt_maps_vertical(args, test_frame, x_grads, pos_sal, neg_sal, label, flow = 'u', scores = None):
    """
    Plot gradient maps, postive, and negative saliency maps that respective to each input frame 
    in vertical axis as temporal timeline
    
    Inputs:
        args : program arguments
        test_frame : input volume of testing clip put into the network
        x_grads : output volume of series of gradient maps
        pos_sal : output volume of series of postive saliency maps
        neg_sal : output volume of series of negative saliency maps
        label : class label index of testing clip
        
    Returns:
        plt : pyplot object containing organized outputs
    """
    
    contents = [test_frame.cpu().detach().numpy(), x_grads, pos_sal, neg_sal]
    titles = ['Original Frame', 'Gradient Map', 'Positive Saliency', 'Negative Saliency']

    col = 4
    row = args.frame_num
    
    fig = plt.figure(figsize = (col * 3, row * 3))
    plt.title(label + ' (' + str(args.test_label + 1) + ')' + 
              ((' s = ' + str(scores)[:6]) if scores is not None else '') + 
              '\n' + str(col - 1) + 
              ((' ' + flow + '_') if args.modality == 'flow' else ' ') + 
              args.modality + ' frames (' + args.test_video + ')\n',
              fontdict = {'fontsize' : 16}, loc = 'left')
    plt.axis('off')
    
    for i in range(0, test_frame.shape[2] * col):
        
        if args.modality == 'rgb':
            index = i // col
        else:
            if flow == 'u':
                index = (i // col) * 2
            else:
                index = (i // col) * 2 + 1
        
        img = contents[i % col][0, :, index].transpose((1, 2, 0))
        img = denormalize_buffer(img, option = 0 if (i % col) == 0 else 1)
        if args.modality == 'flow':
            img = img.reshape(img.shape[:2])
        
        ax = fig.add_subplot(row, col, i + 1)
        if i < 4:
            ax.set_title(titles[i % col])
        
        plt.axis('off')
        if args.modality == 'flow' and (i % col) in [0, 1]:
            plt.imshow(img, cmap = 'gray')
        else:
            plt.imshow(img)
        
    plt.subplots_adjust(hspace=0, wspace=0)
    
    return plt

def plt_maps_horizontal(args, test_frame, x_grads, pos_sal, neg_sal, label, flow = 'u', scores = None):
    """
    Plot gradient maps, postive, and negative saliency maps that respective to each input frame 
    in horizontal axis as temporal timeline
    
    Inputs:
        args : program arguments
        test_frame : input volume of testing clip put into the network
        x_grads : output volume of series of gradient maps
        pos_sal : output volume of series of postive saliency maps
        neg_sal : output volume of series of negative saliency maps
        label : class label index of testing clip
        flow : indicating which direction of flows to visualize
        
    Returns:
        plt : pyplot object containing organized outputs
    """
    
    contents = [test_frame.cpu().detach().numpy(), x_grads, pos_sal, neg_sal]
    titles = ['Original Frame', 'Gradient Map', 'Positive Saliency', 'Negative Saliency']

    col = args.frame_num + 1
    row = 4
    
    fig = plt.figure(figsize = (col * 3, row * 3))
    plt.title(label + ' (' + str(args.test_label + 1) + ')' + 
              ((' s = ' + str(scores)[:6]) if scores is not None else '') + 
              '\n' + str(col - 1) + 
              ((' ' + flow + '_') if args.modality == 'flow' else ' ') + 
              args.modality + ' frames (' + args.test_video + ')\n',
              fontdict = {'fontsize' : 16}, loc = 'left')
    plt.axis('off')
    
    for i in range(0, row):
        
        for j in range(0, col):
            ax = fig.add_subplot(row, col, i * col + j + 1)
            if j > 0:
                
                if args.modality == 'rgb':
                    index = j - 1
                else:
                    if flow == 'u':
                        index = (j - 1) * 2
                    else:
                        index = (j - 1) * 2 + 1
                
                img = contents[i][0, :, index].transpose((1, 2, 0))
                img = denormalize_buffer(img, option = 0 if i == 0 else 1)
                if args.modality == 'flow':
                    img = img.reshape(img.shape[:2])
            else:
                img = np.ones((112, 112, 3)).astype(np.uint8) * 255
                plt.text(0.5, 0.5, titles[i], fontsize = 16,
                         horizontalalignment = 'center', 
                         verticalalignment = 'center', 
                         transform = ax.transAxes)
                #ax.set_title(titles[i], loc = 'center')
                #ax.set_text(0.5, 0.5, titles[i])
            
            plt.axis('off')
            if i in [0, 1] and args.modality == 'flow':
                plt.imshow(img, cmap = 'gray')
            else:
                plt.imshow(img)
        
    plt.subplots_adjust(hspace=0, wspace=0)
    
    return plt

def cv2_maps(args, test_frame, x_grads, pos_sal, neg_sal, label, flow = 'u', scores = None):
    """
    Plot gradient maps, postive, and negative saliency maps that respective to each input frame 
    and shows it as an animation with its temporal timeline in a cv2 window
    
    Inputs:
        args : program arguments
        test_frame : input volume of testing clip put into the network
        x_grads : output volume of series of gradient maps
        pos_sal : output volume of series of postive saliency maps
        neg_sal : output volume of series of negative saliency maps
        label : class label index of testing clip
        flow : indicating which direction of flows to visualize
        
    Returns:
        none
    """
    
    contents = [test_frame.cpu().detach().numpy(), x_grads, pos_sal, neg_sal]
    titles = ['Original Frame', 'Gradient Map', 'Positive Saliency', 'Negative Saliency']
    
    # assgin output image size
    img_h = test_frame.shape[3] * 2
    img_w = test_frame.shape[4] * 2
    
    text_h = 80
    btm_space = 10
    space = 10
    
    out_h = img_h + text_h + btm_space
    out_w = img_w * 4 + 5 * space
    
    output_frames = np.ones((out_h, out_w, 3), np.uint8)
    output_frames *= 255
    
    # draw title
    cv2.putText(output_frames, label + ' (' + str(args.test_label + 1) + ') ' + 
                ((' s = ' + (str(scores)[:6])) if scores is not None else ''), 
                (10, 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0), thickness = 1)
    cv2.putText(output_frames, str(args.frame_num) + 
                ((' ' + flow + '_') if args.modality == 'flow' else ' ') +
                ' frames (' + args.test_video + ')', 
                (10, 35), cv2.FONT_HERSHEY_PLAIN, 0.8, (0, 0, 0))
    
    # draw subtitle
    for i in range(4):
        cv2.putText(output_frames, titles[i], (i * img_w + space * (i + 1), 65), 
                cv2.FONT_HERSHEY_PLAIN, 1, (100, 100, 100), thickness = 1)
    
    # plot contents for each testing frames
    for i in range(args.frame_num):
        
        if args.modality == 'rgb':
            index = i
        else:
            if flow == 'u':
                index = i * 2
            else:
                index = i * 2 + 1
        
        # draw current frame number text
        # rectangle to cover previous text
        cv2.rectangle(output_frames, (out_w - 120, 0), (out_w - 1, 40), (255, 255, 255), cv2.FILLED)
        cv2.putText(output_frames, 'FRAME ' + str(i + 1), 
            (out_w - 120, 30), cv2.FONT_HERSHEY_PLAIN, 1.2, (0, 0, 200), thickness = 2)
        
        for j in range(4):
            # transform contents to be visualizable
            img = contents[j][0, :, index].transpose((1, 2, 0))
            img = cv2.resize(denormalize_buffer(img, option = 0 if j == 0 else 1), (img_h, img_w))
            
            if args.modality == 'rgb':
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            else:
                img = np.expand_dims(img, axis = 2)
            
#            if j in [2, 3] and args.modality == 'flow':
#                cv2.applyColorMap(img, img, cv2.COLORMAP_HSV)
    
            np.copyto(output_frames[text_h : out_h - btm_space, 
                                j * img_w + space * (j + 1) : 
                                    (j + 1) * img_w + space * (j + 1), :], img)
        # show results
        cv2.imshow('RESULT', output_frames)
        cv2.waitKey(1000 if i < args.frame_num - 1 and i > 0 else 0)
    
    cv2.destroyAllWindows()