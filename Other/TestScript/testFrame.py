import cv2
import numpy as np
#script que simula o jogo, pra testar um frame
#se apertar esc ele fecha, se apertar espaço alterna entre uma tela preta e um frame
print("Aperte espaço para mudar frame/tela preta")
print("Pressione uma tecla pra selecionar a resolução:")
print("A->1280x720 zoom = 75%")
print("B->1280x720 zoom = 80%")
print("C->1280x720 zoom = 85%")
print("D->1280x720 zoom = 90%")
print("E->1280x720 zoom = 95%")
print("F->1280x720 zoom = 100%")
print("G->1280x720 zoom = 125%")
print("H->1752x712 zoom = 75%")
print("I->1752x712 zoom = 80%")
print("J->1752x712 zoom = 85%")
print("K->1752x712 zoom = 90%")
print("L->1752x712 zoom = 95%")
print("M->1752x712 zoom = 100%")
print("N->1752x712 zoom = 105%")
print("O->1752x712 zoom = 110%")
print("P->1752x712 zoom = 115%")
print("Q->1752x712 zoom = 120%")
print("R->1752x712 zoom = 125%")
print("S->1920x1080 zoom = 90%")
cv2.imshow('Stardew Valley', np.zeros([20,20]))
k = cv2.waitKey()
if k == 65 or k == 97: # letra a
    img = cv2.imread('1280x720_zoom75.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 66 or k == 98: # letra b
    img = cv2.imread('1280x720_zoom80.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 67 or k == 99: # letra c
    img = cv2.imread('1280x720_zoom85.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 68 or k == 100: # letra d
    img = cv2.imread('1280x720_zoom90.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 69 or k == 101: # letra e
    img = cv2.imread('1280x720_zoom95.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 70 or k == 102: # letra f
    img = cv2.imread('1280x720_zoom100.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 71 or k == 103: # letra g
    img = cv2.imread('1280x720_zoom125.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 72 or k == 104: # letra h
    img = cv2.imread('1752x712_zoom75.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 73 or k == 105: # letra i
    img = cv2.imread('1752x712_zoom80.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 74 or k == 106: # letra j
    img = cv2.imread('1752x712_zoom85.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 75 or k == 107: # letra k
    img = cv2.imread('1752x712_zoom90.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 76 or k == 108: # letra l
    img = cv2.imread('1752x712_zoom95.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 77 or k == 109: # letra m
    img = cv2.imread('1752x712_zoom100.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 78 or k == 110: # letra n
    img = cv2.imread('1752x712_zoom105.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 79 or k == 111: # letra o
    img = cv2.imread('1752x712_zoom110.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 80 or k == 112: # letra p
    img = cv2.imread('1752x712_zoom115.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 81 or k == 113: # letra q
    img = cv2.imread('1752x712_zoom120.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 82 or k == 114: # letra r
    img = cv2.imread('1752x712_zoom125.png')
    img2 = np.zeros(img.shape)
    dsp = img
if k == 83 or k == 115: # letra s
    img = cv2.imread('1920x1080_zoom90.png')
    img2 = np.zeros(img.shape)
    dsp = img


cv2.imshow('Stardew Valley', img)
while True:
    k = cv2.waitKey(0)
    if k == 32:
        if dsp is img:
            dsp = img2
        elif dsp is img2:
            dsp = img
        cv2.imshow('Stardew Valley', dsp)
    elif k == 27:
        cv2.destroyAllWindows()
        break
