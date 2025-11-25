import os
import random
import sys
import time
import pygame as pg



WIDTH, HEIGHT = 1100, 650
DELTA={pg.K_UP:(0,-5), 
       pg.K_DOWN:(0,5), 
       pg.K_LEFT:(-5,0), 
       pg.K_RIGHT:(5,0)
    } 
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとん or 爆弾のRect
    戻り値: タプル（横方向のはみ出し判定結果、縦方向のはみ出し判定結果）
    画面内：True/画面外：False
    """ 
    yoko,tate = True, True
    if rct.left < 0 or WIDTH < rct.right:#横方向のはみ出しチェック
        yoko= False
    if rct.top < 0 or HEIGHT < rct.bottom:#縦方向のはみ出しチェック
        tate= False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """ゲームオーバー画面を表示する関数
    引数: screen 画面Surface
    戻り値: なし
    画面中央に半透明の黒い矩形を表示し、その上に白文字で "Game Over" と表示し、
    こうかとん画像を表示する。
    """
    
    # 1) 黒い矩形を描画するための空のSurfaceを作る
    Surface = pg.Surface((WIDTH, HEIGHT))
    # 2) 黒い矩形を描画して透明度を設定する
    Surface.fill((0, 0, 0))
    Surface.set_alpha(180)  # 0-255 の範囲で透過度を指定

    # 3) 白文字で "Game Over" と書かれたフォントSurfaceを作り、Surfaceにblitする
    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    Surface.blit(text, text_rect)

    # 4) こうかとん画像をロードし、こうかとんSurfaceを作り、overlayにblitする
    try:
        kk_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    except Exception:
        kk_img = None
    if kk_img:
        kk_rect = kk_img.get_rect(center=(WIDTH // 2-240, HEIGHT //2))
        kk_rect2 = kk_img.get_rect(center=(WIDTH // 2+240, HEIGHT // 2))
        Surface.blit(kk_img, kk_rect)
        Surface.blit(kk_img, kk_rect2)

    # 5) Surfaceをscreenにblitする
    screen.blit(Surface, (0, 0))

    # 6) 画面を更新してから5秒間待つ
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """爆弾画像のリストと加速度のリストを作成する関数
    返り値: 
     1. 爆弾Surfaceのリスト
     2. 爆弾の加速度のリスト
    """
    bb_imgs = []          # 爆弾の大きさ違いのSurfaceを入れるリスト
    bb_accs = [a for a in range(1, 11)]   # 加速度のリスト（1〜10）

    for r in range(1, 11):      # 1〜10段階の大きさを作成
        size = 20 * r
        bb_img = pg.Surface((size, size), pg.SRCALPHA)  # 透明背景のSurface
        
        pg.draw.circle(bb_img,(255, 0, 0),(size // 2, size // 2), size // 2)
        bb_imgs.append(bb_img)

    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """こうかとん画像の辞書を作成する関数
    戻り値: 方向キーの組み合わせをキー、対応するこうかとんSurfaceを値とする辞書
    """
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_img_f = pg.transform.flip(kk_img, True, False)

    kk_dict = {
        (0,5): pg.transform.rotozoom(kk_img, 90, 1.0),     # 下
        (0,-5): pg.transform.rotozoom(kk_img, 180, 1.0),  # 上
        (5,0): pg.transform.flip(kk_img, True, False),    # 右
        (-5,0): kk_img,   # 左
        (5,5): pg.transform.rotozoom(kk_img, 135, 1.0),    # 右下
        (5,-5): pg.transform.rotozoom(kk_img_f, 45, 1.0),  # 右上
        (-5,5): pg.transform.rotozoom(kk_img_f, 225, 1.0), # 左下
        (-5,-5): pg.transform.rotozoom(kk_img, 315, 1.0),# 左上
        (0,0): kk_img      # 静止
    }
    return kk_dict
        

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    bb_img = pg.Surface((20, 20)) #空のSurface
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10) #半径10の赤い円を描く
    bb_img.set_colorkey((0, 0, 0))#黒色の部分を透明にする
    bb_rct= bb_img.get_rect()#爆弾Rect
    bb_rct.centerx = random.randint(0, WIDTH)#爆弾の縦座標
    bb_rct.centery = random.randint(0, HEIGHT)#爆弾の横座標
    vx, vy = +5, +5#爆弾の移動速度
    clock = pg.time.Clock()
    tmr = 0
    bb_imgs, bb_accs = init_bb_imgs()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return

        if kk_rct.colliderect(bb_rct):#こうかとんと爆弾が重なったら
            print("ゲームオーバー")
            gameover(screen)
            return

        idx = min(tmr // 500, 9)
        avx = vx*bb_accs[idx]
        avy = vy*bb_accs[idx]
        bb_rct.move_ip(avx, avy)
        
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]


        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]#横方向の移動量
                sum_mv[1] += mv[1]#縦方向の移動量 
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct.move(sum_mv)) != (True, True):#画面外なら
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])#移動をなかったことにする
        yoko, tate = check_bound(bb_rct)
        if yoko == False:
            vx *= -1
        if tate == False:
            vy *= -1
        bb_rct.move_ip(vx, vy)
        kk_dict= get_kk_imgs()
        kk_img = kk_dict[tuple(sum_mv)]
        screen.blit(kk_img, kk_rct)
        screen.blit(bb_imgs[idx], bb_rct)
        bb_rct.width  = bb_imgs[idx].get_rect().width
        bb_rct.height = bb_imgs[idx].get_rect().height
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
