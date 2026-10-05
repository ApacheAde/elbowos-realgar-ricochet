#!/usr/bin/env python3
"""Realgar Ricochet — neon ember-canyon arcade for ElbowOS. Python 3 + pygame."""
import math, os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/REALGAR_RICOCHET_ElbowOS.mp4")
BG, EMBER, ASH, GOLD = (12, 8, 10), (255, 78, 28), (255, 168, 64), (255, 214, 90)
SLAG, MINT, INK = (255, 64, 96), (120, 255, 190), (18, 8, 8)

class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        try:
            self.screen = pygame.display.set_mode((W, H), 0 if PLAY else pygame.HIDDEN)
        except pygame.error:
            self.screen = pygame.Surface((W, H))
        pygame.display.set_caption("Realgar Ricochet")
        self.big = pygame.font.SysFont("dejavusans", 64, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 40, bold=True)
        self.tiny = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.streak = 0
        self.px = W / 2
        self.ball = [W / 2, 720.0]
        self.vel = [7.5, -11.0]
        self.trail = []
        self.sparks = []
        self.nodes = []
        self.rng = random.Random(19)
        self.seed_nodes()

    def seed_nodes(self):
        self.nodes = []
        for i in range(8):
            side = -1 if i % 2 == 0 else 1
            self.nodes.append({
                "x": 150 if side < 0 else W - 150,
                "y": 420 + i * 130,
                "r": 28,
                "hot": True,
                "cool": 0,
                "side": side,
            })

    def pop(self, x, y, col, n=8):
        for k in range(n):
            ang = k / n * math.tau
            self.sparks.append([x, y, math.cos(ang) * 6, math.sin(ang) * 6, col, 14])

    def update(self, auto=False):
        self.t += 1
        if auto:
            aim = self.ball[0] + self.vel[0] * 6
            self.px += max(-28, min(28, aim - self.px))
        self.px = max(170, min(W - 170, self.px))
        self.ball[0] += self.vel[0]
        self.ball[1] += self.vel[1]
        self.vel[1] += 0.18
        if self.ball[0] < 120:
            self.ball[0] = 120
            self.vel[0] = abs(self.vel[0]) + 0.3
            self.pop(self.ball[0], self.ball[1], ASH, 5)
        if self.ball[0] > W - 120:
            self.ball[0] = W - 120
            self.vel[0] = -abs(self.vel[0]) - 0.3
            self.pop(self.ball[0], self.ball[1], ASH, 5)
        if self.ball[1] < 340:
            self.ball[1] = 340
            self.vel[1] = abs(self.vel[1])
        pad_y = 1560
        if self.ball[1] > pad_y - 24 and self.vel[1] > 0 and abs(self.ball[0] - self.px) < 130:
            self.ball[1] = pad_y - 24
            self.vel[1] = -abs(self.vel[1]) - 0.4
            self.vel[0] += (self.ball[0] - self.px) * 0.08
            self.score += 15
            self.pop(self.ball[0], pad_y, GOLD, 6)
        if self.ball[1] > 1700:
            self.score = max(0, self.score - 40)
            self.streak = 0
            self.ball = [self.px, 900.0]
            self.vel = [self.rng.choice([-8, 8]), -12]
            self.pop(self.px, 1640, SLAG, 10)
        spd = math.hypot(*self.vel)
        if spd > 22:
            self.vel[0] *= 22 / spd
            self.vel[1] *= 22 / spd
        for n in self.nodes:
            if n["cool"] > 0:
                n["cool"] -= 1
                if n["cool"] == 0:
                    n["hot"] = True
                    n["y"] = 420 + self.rng.randrange(0, 8) * 110
                continue
            if n["hot"] and math.hypot(self.ball[0] - n["x"], self.ball[1] - n["y"]) < n["r"] + 22:
                n["hot"] = False
                n["cool"] = 36
                self.streak += 1
                self.score += 100 + self.streak * 10
                self.vel[0] += n["side"] * -4
                self.vel[1] = -abs(self.vel[1]) - 1
                self.pop(n["x"], n["y"], EMBER, 12)
        self.trail.append((self.ball[0], self.ball[1]))
        self.trail = self.trail[-18:]
        nxt = []
        for p in self.sparks:
            p[0] += p[2]
            p[1] += p[3]
            p[5] -= 1
            if p[5] > 0:
                nxt.append(p)
        self.sparks = nxt

    def draw(self, surf):
        surf.fill(BG)
        for i in range(14):
            pygame.draw.line(surf, (42, 16, 14), (0, 300 + i * 110), (W, 340 + i * 110), 2)
        pygame.draw.rect(surf, (28, 12, 10), (70, 300, 940, 1360), border_radius=36)
        pygame.draw.rect(surf, EMBER, (70, 300, 940, 1360), 6, border_radius=36)
        pygame.draw.rect(surf, (48, 18, 14), (0, 0, 90, H))
        pygame.draw.rect(surf, (48, 18, 14), (W - 90, 0, 90, H))
        title = self.big.render("REALGAR RICOCHET", True, EMBER)
        surf.blit(title, title.get_rect(center=(W // 2, 90)))
        sub = self.tiny.render("KEEP THE EMBER  \u00b7  POP THE VEINS", True, ASH)
        surf.blit(sub, sub.get_rect(center=(W // 2, 155)))
        sc = self.mid.render(f"SCORE  {self.score}", True, GOLD)
        surf.blit(sc, sc.get_rect(center=(W // 2, 230)))
        for n in self.nodes:
            col = EMBER if n["hot"] else (70, 40, 36)
            pygame.draw.circle(surf, col, (int(n["x"]), int(n["y"])), n["r"])
            pygame.draw.circle(surf, GOLD if n["hot"] else (90, 60, 50), (int(n["x"]), int(n["y"])), n["r"], 4)
            if n["hot"]:
                pygame.draw.circle(surf, (255, 230, 180), (int(n["x"] - 6), int(n["y"] - 6)), 6)
        if len(self.trail) > 1:
            pygame.draw.lines(surf, ASH, False, [(int(x), int(y)) for x, y in self.trail], 6)
        bx, by = int(self.ball[0]), int(self.ball[1])
        pygame.draw.circle(surf, EMBER, (bx, by), 22)
        pygame.draw.circle(surf, GOLD, (bx, by), 22, 3)
        pygame.draw.circle(surf, (255, 240, 200), (bx - 6, by - 6), 5)
        pygame.draw.rect(surf, ASH, (int(self.px) - 110, 1560, 220, 28), border_radius=12)
        pygame.draw.rect(surf, GOLD, (int(self.px) - 110, 1560, 220, 28), 3, border_radius=12)
        for x, y, vx, vy, col, life in self.sparks:
            pygame.draw.circle(surf, col, (int(x), int(y)), max(2, life // 3))
        st = self.mid.render(f"STREAK  {self.streak}", True, MINT)
        surf.blit(st, st.get_rect(center=(W // 2, 1690)))
        hint = self.tiny.render("A / D  slide scoop     R  reset", True, (230, 180, 160))
        surf.blit(hint, hint.get_rect(center=(W // 2, 1764)))
        brand = self.mid.render("x.com/ElbowOS", True, (255, 220, 200))
        surf.blit(brand, brand.get_rect(center=(W // 2, 1846)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.px -= 18
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.px += 18
            self.update(False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = ["ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", OUT]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for _ in range(FPS * SECS):
                self.update(True)
                self.draw(self.screen)
                proc.stdin.write(pygame.image.tobytes(self.screen, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT)
        pygame.quit()

def main():
    g = Game()
    g.play_interactive() if PLAY and not RECORD else g.record()

if __name__ == "__main__":
    main()
