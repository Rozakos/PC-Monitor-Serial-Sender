"""Core logic tests (no hardware, no Windows needed):  python -m unittest discover tests

Expected LCD rows were produced by compiling the real firmware
(Arduino-PC-Monitor-1602 / -2004 src/main.cpp) natively with stubbed Arduino
libraries; '#' = filled bar cell, '.' = empty.
"""
import os, sys, queue, threading, time, unittest
os.environ.setdefault("PYSTRAY_BACKEND", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main as m


def stats(cpu=42.3, ram=58.7, gpu=73.5, ct=56.5, gt=48.0, ramu=9381, ramt=16384,
          vram=5300, vramt=12288, dl=45, ul=12, link=1000):
    return {"cpu": cpu, "ram": ram, "gpu": gpu, "cpu_temp": ct, "gpu_temp": gt,
            "ram_mb": ramu, "ram_total_mb": ramt, "vram_mb": vram, "vram_total_mb": vramt,
            "dl_kb": dl, "ul_kb": ul, "link_speed": link}

def show(rows):
    return [r.replace(m._BAR_ON, "#").replace(m._BAR_OFF, ".") for r in rows]


class PreviewMatchesFirmware(unittest.TestCase):
    def test_1602_cpu(self):
        self.assertEqual(show(m.render_1602(0, stats())), ["CPU  42%  56.5°C", "######.........."])

    def test_1602_gpu_no_sensor_uses_decimal_branch(self):
        # firmware: (gput10 % 10 != 0) is true for -1, so it prints " --.-"
        self.assertEqual(show(m.render_1602(1, stats(gpu=100, gt=-1)))[0], "GPU 100%   --.- ")

    def test_1602_gpu_small_vram(self):
        self.assertEqual(show(m.render_1602(1, stats(gpu=12, gt=48.0, vram=512, vramt=2048)))[0],
                         "GPU 0.5/2G  48°C")

    def test_1602_net_split_bar(self):
        # 16 columns: the firmware's last "K" falls off the edge
        self.assertEqual(show(m.render_1602(3, stats(dl=62500, ul=0, link=1000))),
                         ["DL:  61M UL:   0", "####............"])

    def test_2004_gpu_block(self):
        self.assertEqual(show(m.render_2004_block(1, stats())),
                         ["GPU  73% 5/12G  48°C", "##############......"])

    def test_2004_screen_two_blocks(self):
        rows = m.screen_rows("2004", [0, 2], 0, stats())
        self.assertEqual(len(rows), 4)
        self.assertTrue(rows[0].startswith("CPU") and rows[2].startswith("RAM"))


class PageDistribution(unittest.TestCase):
    def test_one_page_per_screen_last_rotates(self):
        self.assertEqual(m.distribute_pages(2, [0, 1, 2, 3]), [[0], [1, 2, 3]])
        self.assertEqual(m.distribute_pages(4, [2, 0]), [[2], [0], [], []])
        self.assertEqual(m.distribute_pages(0, [0]), [])


class TypeperfParsing(unittest.TestCase):
    OUT = ('"(PDH-CSV 4.0)","\\\\PC\\GPU Engine(pid_1_eng_0_engtype_3D)\\Utilization Percentage",'
           '"\\\\PC\\GPU Engine(pid_2_eng_0_engtype_3D)\\Utilization Percentage",'
           '"\\\\PC\\GPU Engine(pid_1_eng_2_engtype_Copy)\\Utilization Percentage",'
           '"\\\\PC\\GPU Process Memory(pid_1)\\Dedicated Usage"\n'
           '"10/11/2026 03:10:00.123","40.25","12.0","30.0","1610612736.0"\n'
           'Exiting, please wait...\n')

    def test_busiest_engine_type_and_vram(self):
        orig = m.subprocess.check_output
        m.subprocess.check_output = lambda *a, **k: self.OUT.encode()
        try:
            self.assertEqual(m.get_gpu_counters(), (52.25, 1536))
        finally:
            m.subprocess.check_output = orig


class FrameFormat(unittest.TestCase):
    def test_frame_field_order(self):
        t = m.MonitorThread.__new__(m.MonitorThread)
        t.cfg = {"page_delay": 3000, "lcd_types": {"0x26": "2004", "0x27": "1602"}}
        t.page_order, t.mask, t.ram_total, t.vram_total, t.link_speed = [2, 0], 5, 16384, 12288, 1000
        self.assertEqual(
            t._frame(stats()),
            "CPU=423;RAM=587;GPU=735;DL=45;UL=12;RAMU=9381;RAMT=16384;VRAM=5300;VRAMT=12288;"
            "TEMP=565;GPUT=480;LSPD=1000;PG=5;PDLY=3000;PGORD=2,0;LCD2004=38\r\n")


if __name__ == "__main__":
    unittest.main()
