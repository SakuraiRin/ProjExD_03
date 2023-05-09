import random
import sys
import time
import pygame as pg
WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
def check_bound(area: pg.Rect, obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数1 area：画面SurfaceのRect
    引数2 obj：オブジェクト（爆弾，こうかとん）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < area.left or area.right < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < area.top or area.bottom < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def check_collide(obj1: "Bird|Bomb", obj2: "Bird|Bomb") -> bool:
    """
    2つのオブジェクトの衝突を判定し，真理値を返す
    引数1 obj1：BirdまたはBombオブジェクト
    引数2 obj1：BirdまたはBombオブジェクト
    戻り値：衝突判定結果（衝突している：True／衝突してない：False）
    """
    rct1 = obj1.get_rct()
    rct2 = obj2.get_rct()
    if rct1.colliderect(rct2):
        return True
    else:
        return False


class Bird:
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    _delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }
    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        self._img = pg.transform.flip(  # 左右反転
            pg.transform.rotozoom(  # 2倍に拡大
                pg.image.load(f"ex03/fig/{num}.png"), 
                0, 
                2.0), 
            True, 
            False
        )
        self._rct = self._img.get_rect()
        self._rct.center = xy
    def change_img(self, num: int, screen: pg.Surface, sec: int):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)
        pg.display.update()
        time.sleep(sec)
    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        for k, mv in __class__._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
        if check_bound(screen.get_rect(), self._rct) != (True, True):
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        screen.blit(self._img, self._rct)

    def check_collide(self, bb: "Bomb") -> bool:
        if self._rct.colliderect(bb._rct):
            return True
        else:
            return False
    def get_rct(self) -> pg.Rect:
        return self._rct


class Bomb:
    """
    爆弾に関するクラス
    """
    def __init__(self, color: tuple[int, int, int], rad: int):
        """
        引数に基づき爆弾円Surfaceを生成する
        引数1 color：爆弾円の色タプル
        引数2 rad：爆弾円の半径
        """
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = +1, +1
    def update(self, screen: pg.Surface):
        """
        爆弾を速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        yoko, tate = check_bound(screen.get_rect(), self._rct)
        if not yoko:
            self._vx *= -1
        if not tate:
            self._vy *= -1
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)

    def get_rct(self) -> pg.Rect:
        return self._rct


def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bomb = Bomb((255, 0, 0), 10)
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
        tmr += 1
        screen.blit(bg_img, [0, 0])

        if bird.check_collide(bomb):
        if check_collide(bird, bomb):
            bird.change_img(8, screen, 1)  # こうかとん画像を8.pngに切り替え，1秒間表示させる
            return

        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        bomb.update(screen)
        pg.display.update()
        clock.tick(1000)
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()