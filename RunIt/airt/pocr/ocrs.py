# import asyncio
# import uvloop
import time
import ddddocr
import easyocr
from init import config
from poker_cards import *
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
# uvloop.install()

# reader = easyocr.Reader(['ch_sim','en'])
reader = easyocr.Reader(['en'])

CONF = config['COLOR']
ocr = ddddocr.DdddOcr()

def easyocr_poker(filename):
    result = reader.readtext(filename, detail=0)
    if not result:
        return None
    result = result[0].upper()
    if result not in POKER_SCOPE:
        return None
    return result

def ddddocr_poker(filename):
    with open(filename, 'rb') as f:
        image_bytes = f.read()
    res = ocr.classification(image_bytes)
    result = res.upper()
    print(f'{filename}--OCR识别最初: {result}')
    if 'I' in result:
        result = result.replace('I', '1')
    if 'O' in result:
        result = result.replace('O', '0')
    if '0' in result and '1' not in result:
        result = result.replace('0', 'Q')
    if 'TD' in result:
        result = result.replace('TD', 'Q')
    for res in POKER_SCOPE:
        if res in result:
            result = res
    # if 'D' in result:
    #     result = result.replace('D', 'Q')
    # if 'U' in result:
    #     result = result.replace('U', 'Q')
    if result == '1':
        result = '10'
    if 'D' in result:
        easy_result = easyocr_poker(filename)
        print(f'easy result: {result}')
        if easy_result != result and easy_result:
            result = easy_result
    if result in POKER_SCOPE:
        print(f'POKER_SCOPE result: {result}')
        return result
    else:
        return None

def poker_ocr(filename):
    # num1 = await asyncio.create_task(ddddocr_poker(filename))
    num1 = ddddocr_poker(filename)
    print(f'ddddocr_poker: {num1}')
    # num2 = easyocr_poker(filename)
    # print(f'easyocr_poker: {num2}')
    # if num1 == num2:
    #     num = num1
    # else:
    #     if num1 and not num2:
    #         num = num1
    #     else:
    #         num = num2
    # return num

if __name__ == '__main__':
    start = time.time()
    f1 = '/Users/antx/Code/tmp/airt/pics/playing/3537303880339554304/PLAYER1/HEAD/1.png'
    num = ddddocr_poker(f1)
    print(num)
    end = time.time()
    print(f'耗时：{end - start}s.')
