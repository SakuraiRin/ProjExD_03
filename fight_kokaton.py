import math
import random
import sys
import time
import pygame as pg
WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ
NUM_OF_BOMBS = 5
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
        img0 = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self._imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self._dire = (+1, 0)
        self._img = self._imgs[self._dire]
        self._rct = self._img.get_rect()
        self._rct.center = xy
    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/{num}.png"), 0, 2.0)
        screen.blit(self._img, self._rct)
    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__._delta.items():
            if key_lst[k]:
                self._rct.move_ip(mv)
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(screen.get_rect(), self._rct) != (True, True):
            for k, mv in __class__._delta.items():
                if key_lst[k]:
                    self._rct.move_ip(-mv[0], -mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self._dire = tuple(sum_mv)
            self._img = self._imgs[self._dire] 
        screen.blit(self._img, self._rct)
        
    def get_rct(self) -> pg.Rect:
        return self._rct
    
    def get_direction(self) -> tuple[int, int]:
        return self._dire
    
class Bomb:
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
    dires = [-1, +1]
    """
    爆弾に関するクラス
    """
    def __init__(self):
        """
        爆弾円Surfaceを生成する
        """
        rad = random.randint(10, 50)
        color = random.choice(__class__.colors)
        self._img = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self._img, color, (rad, rad), rad)
        self._img.set_colorkey((0, 0, 0))
        self._rct = self._img.get_rect()
        self._rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        self._vx, self._vy = random.choice(__class__.dires), random.choice(__class__.dires)
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
class Beam:
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        """
        self._vx, self._vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self._vy, self._vx))
        self._img = pg.transform.rotozoom(pg.image.load(f"ex03/fig/beam.png"), angle, 2.0)
        self._rct = self._img.get_rect()
        bird_rct = bird.get_rct()
        self._rct.centery = bird_rct.centery+bird_rct.height*self._vy
        self._rct.centerx = bird_rct.centerx+bird_rct.width*self._vx
    def update(self, screen: pg.Surface):
        """
        ビームを速度ベクトルself._vx, self._vyに基づき移動させる
        引数 screen：画面Surface
        """
        self._rct.move_ip(self._vx, self._vy)
        screen.blit(self._img, self._rct)
    def get_rct(self) -> pg.Rect:
        return self._rct
class Explosion:
    """
    爆発に関するクラス
    """
    def __init__(self, obj: Bomb, life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombインスタンス
        引数2 life：爆発時間
        """
        img = pg.image.load("ex03/fig/explosion.gif")
        self._imgs = [img, pg.transform.flip(img, 1, 1)]
        self._img = self._imgs[0]
        self._rct = self._img.get_rect(center=obj.get_rct().center)
        self._life = life
    def update(self, screen: pg.Surface):
        """
        爆発時間を1減算した爆発経過時間に応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self._life -= 1
        self._img = self._imgs[self._life//10%2]
        screen.blit(self._img, self._rct)
    def get_life(self):
        return self._life
class Score:
    """
    打ち落とした爆弾の数をスコアとして表示するクラス
    """
    def __init__(self):
        self._font = pg.font.Font(None, 50)
        self._color = (0, 0, 255)
        self._score = 0
        self._img = self._font.render(f"Score: {self._score}", 0, self._color)
        self._rct = self._img.get_rect()
        self._rct.center = 100, HEIGHT-50
    def score_up(self):
        self._score += 1
    def update(self, screen: pg.Surface):
        self._img = self._font.render(f"Score: {self._score}", 0, self._color)
        screen.blit(self._img, self._rct)
def main():
    pg.display.set_caption("たたかえ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    bg_img = pg.image.load("ex03/fig/pg_bg.jpg")
    bird = Bird(3, (900, 400))
    bombs = [Bomb() for _ in range(5)]
    beams: list[Beam] = list()
    exps: list[Explosion] = list()
    score = Score()
    tmr = 0
    while True:
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.append(Beam(bird))
                beams.append(Beam(bird))

        tmr += 1
        screen.blit(bg_img, [0, 0])
        
        for j, beam in enumerate(beams):
            if check_bound(screen.get_rect(), beam.get_rct()) != (True, True):
                del beams[j]
            beam.update(screen)
        for i, bomb in enumerate(bombs):
            bomb.update(screen)
            if check_collide(bomb, bird):
                bird.change_img(8, screen)
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return
            for j, beam in enumerate(beams):
                if check_collide(beam, bomb):
                    exps.append(Explosion(bomb, 120))
                    del bombs[i]
                    del beams[j]                    
                    score.score_up()
                    bird.change_img(6, screen)
        for i, exp in enumerate(exps):
            exp.update(screen)
            if exp.get_life() <= 0:
                del exps[i]
        key_lst = pg.key.get_pressed()
        bird.update(key_lst, screen)
        score.update(screen)
        pg.display.update()
        clock.tick(1000)
if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()