import string
import pandas
from PIL import Image
import numpy as np
import csv
from random import randrange

paths = {'mani': './reference/manipulation/NC2016-manipulation-ref.csv',
         'removal': './reference/remove/NC2016-removal-ref.csv',
         'splice': './reference/splice/NC2016-splice-ref.csv'
         }
globalIdx = 0
SavePath = '../NIST2016_Crop/'
TargetSize = 512
TableOfContent = []
selected = []
img_path = "./probe/NC2016_0016.jpg"

img = Image.open(img_path)
x, y = img.size

matrix = 512
sample = 10
sample_list = []

original_path = 'crop'
resize_path = 'resize'


# for i in range(sample):
#     x1 = randrange(0, x - matrix)
#     y1 = randrange(0, y - matrix)
#     crop_img = img.crop((x1, y1, x1 + matrix, y1 + matrix))
#     crop_img.save('{}/{}_{}'.format(original_path, i, 'NC2016_0016.jpg'))
# mani removal splice
def CropByTask(taskID: string, idx):
    print('--Start task {}---'.format(taskID))
    table = pandas.read_csv(paths[taskID], sep="|")
    # =====pictures with masks=====
    manupilated = table[table['IsTarget'] == 'Y']
    manupilated = manupilated[['ProbeFileName', 'ProbeMaskFileName']]
    length = len(manupilated)
    for i in range(length):
        if i % 50 == 0:
            print('{:.4f}% Has done'.format(i / len(manupilated) * 100))

        image_dir = manupilated.iloc[i]['ProbeFileName']
        print(image_dir)
        if image_dir in selected:
            continue
        else:
            mask_dir = manupilated.iloc[i]['ProbeMaskFileName']
            selected.append(image_dir)

            image = Image.open(image_dir)
            # image = Image.open('./probe/NC2016_0623.jpg')
            mask = Image.open(mask_dir)
            (x, y) = image.size
            if x <= matrix or y <= matrix:  # 部分图片过小，不裁剪直接丢弃
                continue
            # 考虑样本均衡，确保有mask和无mask数量一致
            mask_cnt = no_mask_cnt = 5
            j = 0
            while mask_cnt > 0 or no_mask_cnt > 0:
            # for i in range(sample):
                j += 1
                if j == 100:
                    break
                x1 = randrange(0, x - matrix)
                y1 = randrange(0, y - matrix)
                crop_img = image.crop((x1, y1, x1 + matrix, y1 + matrix))
                # crop_img.save('{}/{}_{}'.format(original_path, i, 'NC2016_0016.jpg'))
                # y = int(y / x * 512)
                # image = image.resize((TargetSize, y), Image.ANTIALIAS)
                crop_img_name = '{}.jpg'.format(idx)
                crop_img.save('{}{}.jpg'.format(SavePath, idx))

                crop_mask = mask.crop((x1, y1, x1 + matrix, y1 + matrix))
                # 此处需判断剪裁的mask是否包含真正的mask。
                crop_mask = crop_mask.convert("1")
                mask_np = np.asarray(crop_mask)
                # 分为3种情况，no mask,2%以下：丢弃；2%以上
                mask_pcrt = mask_np.sum()/mask_np.size
                if mask_pcrt < 0.98 and mask_cnt > 0:  # mask区域至少zan
                    mask_name = '{}_mask.jpg'.format(idx)
                    crop_mask.save('{}{}_mask.jpg'.format(SavePath, idx))
                    mask_cnt -= 1
                elif mask_pcrt == 1.0 and no_mask_cnt > 0 :
                    mask_name = 'N'
                    no_mask_cnt -= 1
                else:
                    continue

                idx += 1
                TableOfContent.append([crop_img_name, mask_name, taskID])
    return idx


def decodeNist():
    globalIdx = 0
    globalIdx = CropByTask("splice", globalIdx)
    globalIdx = CropByTask("removal", globalIdx)
    globalIdx = CropByTask("mani", globalIdx)
    with open("{}index.csv".format(SavePath), 'w', newline="") as f:
        writer = csv.writer(f)
        writer.writerows(TableOfContent)


if __name__ == '__main__':
    decodeNist()