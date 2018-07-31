import numpy as np
import os
import torch
import torchvision 
import skvideo.io
import skimage.transform
from utils import to_var
from reader import readShortVideo
from reader import getVideoList

#filepath = 'HW5_data/TrimmedVideos/video/train'
#tag_path = 'HW5_data/TrimmedVideos/label/gt_train.csv'


def get_data(video_path, tag_path, model):
    if torch.cuda.is_available():
        model.cuda()
    file_dict = getVideoList(tag_path)
    x, y = [], []
    print(len(file_dict['Video_index']))
    with torch.no_grad():
        for i in range(len(file_dict['Video_index'])):
            frames = readShortVideo(video_path, file_dict['Video_category'][i],file_dict['Video_name'][i])
            if frames.shape[0] > 120:
                output_1 = model(torch.from_numpy(frames[0:120,:,:,:]).cuda()).detach().cpu().reshape(-1, 512*7*7)
                output_2 = model(torch.from_numpy(frames[120:,:,:,:]).cuda()).detach().cpu().reshape(-1, 512*7*7)
                output = torch.cat((output_1, output_2), 0)
            else:
                output = model(torch.from_numpy(frames).cuda()).detach().cpu().reshape(-1, 512*7*7)
            output = torch.mean(output, 0).numpy()

            x.append(output)
            y.append(int(file_dict['Action_labels'][i]))
            print('\rreading image from {}...{}'.format(video_path,i),end='')

    print('\rreading image from {}...finished'.format(video_path))
    
    return np.array(x).astype(np.float32), np.array(y).astype(np.uint8)


def main():
    train_videopath = 'HW5_data/TrimmedVideos/video/train'
    train_tagpath = 'HW5_data/TrimmedVideos/label/gt_train.csv'
    valid_videopath = 'HW5_data/TrimmedVideos/video/valid'
    valid_tagpath = 'HW5_data/TrimmedVideos/label/gt_valid.csv'

    print('loading VGG16 model...')
    model = torchvision.models.vgg16(pretrained=True).features
    
    x_train, y_train = get_data(train_videopath, train_tagpath, model)
    x_valid, y_valid = get_data(valid_videopath, valid_tagpath, model)

    np.save('data/x_train_vgg16.npy', x_train)
    np.save('data/y_train_vgg16.npy', y_train)
    np.save('data/x_valid_vgg16.npy', x_valid)
    np.save('data/y_valid_vgg16.npy', y_valid)
    

if __name__ == '__main__':
    main()
