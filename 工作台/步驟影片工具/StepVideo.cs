using System;
using System.Collections;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.Drawing.Text;
using System.IO;
using System.Web.Script.Serialization;

// 步驟教學影片產生器：截圖＋游標動畫＋紅圈／框／按鍵提示＋下方字卡，輸出逐格 PNG 給 ffmpeg 合成。
public static class StepVideo
{
    static int W, H, BAND, FPS;
    static Dictionary<string, Bitmap> cache = new Dictionary<string, Bitmap>();
    static string FONT = "Microsoft JhengHei";
    static Color RED = Color.FromArgb(239, 68, 68);
    static Color NAVY = Color.FromArgb(30, 27, 75);
    static Color AMBER = Color.FromArgb(251, 191, 36);

    static double D(object o) { return Convert.ToDouble(o); }
    static double G(Dictionary<string, object> d, string k, double def) { return d.ContainsKey(k) && d[k] != null ? D(d[k]) : def; }
    static string S(Dictionary<string, object> d, string k) { return d.ContainsKey(k) && d[k] != null ? d[k].ToString() : null; }
    static List<Dictionary<string, object>> L(Dictionary<string, object> d, string k)
    {
        var r = new List<Dictionary<string, object>>();
        if (!d.ContainsKey(k) || d[k] == null) return r;
        foreach (var o in (IEnumerable)d[k]) r.Add((Dictionary<string, object>)o);
        return r;
    }
    static Bitmap Img(string p)
    {
        if (!cache.ContainsKey(p)) cache[p] = new Bitmap(p);
        return cache[p];
    }
    static double Ease(double t) { t = Math.Max(0, Math.Min(1, t)); return t < .5 ? 4 * t * t * t : 1 - Math.Pow(-2 * t + 2, 3) / 2; }
    static double Clamp01(double t) { return Math.Max(0, Math.Min(1, t)); }

    public static int Render(string specPath, string outDir)
    {
        var js = new JavaScriptSerializer(); js.MaxJsonLength = int.MaxValue;
        var spec = js.Deserialize<Dictionary<string, object>>(File.ReadAllText(specPath, System.Text.Encoding.UTF8));
        W = (int)G(spec, "w", 1280); H = (int)G(spec, "h", 720); BAND = (int)G(spec, "band", 140); FPS = (int)G(spec, "fps", 25);
        var scenes = L(spec, "scenes");
        Directory.CreateDirectory(outDir);
        int frame = 0;
        Bitmap prevLast = null;
        foreach (var sc in scenes)
        {
            double dur = G(sc, "dur", 4);
            int n = (int)Math.Round(dur * FPS);
            for (int i = 0; i < n; i++)
            {
                double t = (double)i / FPS;
                using (var bmp = new Bitmap(W, H + BAND, PixelFormat.Format24bppRgb))
                using (var g = Graphics.FromImage(bmp))
                {
                    g.SmoothingMode = SmoothingMode.AntiAlias;
                    g.TextRenderingHint = TextRenderingHint.AntiAliasGridFit;
                    g.InterpolationMode = InterpolationMode.HighQualityBicubic;
                    DrawScene(g, sc, t, dur);
                    // 場景開頭 0.3 秒從上一場景淡入
                    if (prevLast != null && t < 0.3)
                    {
                        var cm = new ColorMatrix(); cm.Matrix33 = (float)(1 - t / 0.3);
                        var ia = new ImageAttributes(); ia.SetColorMatrix(cm);
                        g.DrawImage(prevLast, new Rectangle(0, 0, W, H + BAND), 0, 0, W, H + BAND, GraphicsUnit.Pixel, ia);
                    }
                    bmp.Save(Path.Combine(outDir, string.Format("f{0:D5}.png", frame++)), ImageFormat.Png);
                    if (i == n - 1) { if (prevLast != null) prevLast.Dispose(); prevLast = (Bitmap)bmp.Clone(); }
                }
            }
        }
        return frame;
    }

    static void DrawScene(Graphics g, Dictionary<string, object> sc, double t, double dur)
    {
        if (S(sc, "type") == "title") { DrawTitle(g, sc, t); return; }
        // 背景截圖（可依時間切換）
        string img = S(sc, "img");
        foreach (var sw in L(sc, "imgs")) if (t >= G(sw, "t", 0)) img = S(sw, "img");
        if (sc.ContainsKey("chrome")) { g.DrawImage(Img(img), new Rectangle(0, 80, W, H - 80)); DrawChrome(g, (Dictionary<string, object>)sc["chrome"], t); }
        else g.DrawImage(Img(img), new Rectangle(0, 0, W, H));

        foreach (var b in L(sc, "dims")) DrawDim(g, b, t);
        foreach (var b in L(sc, "snip")) DrawSnip(g, b, t);
        foreach (var b in L(sc, "boxes")) DrawBox(g, b, t);
        foreach (var b in L(sc, "typing")) DrawTyping(g, b, t);
        foreach (var b in L(sc, "circles")) DrawCircle(g, b, t);
        foreach (var b in L(sc, "labels")) DrawLabel(g, b, t);
        foreach (var b in L(sc, "keys")) DrawKeys(g, b, t);
        foreach (var b in L(sc, "toasts")) DrawToast(g, b, t);
        foreach (var b in L(sc, "clicks")) DrawClick(g, b, t);
        DrawCursor(g, L(sc, "cursor"), t);
        DrawBand(g, sc, t);
    }

    static bool Live(Dictionary<string, object> b, double t, out double lt)
    {
        double st = G(b, "t", 0), du = G(b, "dur", 999);
        lt = t - st;
        return t >= st && t < st + du;
    }

    static void DrawTitle(Graphics g, Dictionary<string, object> sc, double t)
    {
        using (var br = new LinearGradientBrush(new Rectangle(0, 0, W, H + BAND), Color.FromArgb(79, 70, 229), Color.FromArgb(14, 116, 144), 45f))
            g.FillRectangle(br, 0, 0, W, H + BAND);
        float a = (float)Clamp01(t / 0.5);
        var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
        using (var f1 = new Font(FONT, 54, FontStyle.Bold, GraphicsUnit.Pixel))
        using (var f2 = new Font(FONT, 30, FontStyle.Regular, GraphicsUnit.Pixel))
        using (var b1 = new SolidBrush(Color.FromArgb((int)(255 * a), Color.White)))
        using (var b2 = new SolidBrush(Color.FromArgb((int)(220 * a), 224, 231, 255)))
        {
            float cy = (H + BAND) / 2f;
            g.DrawString(S(sc, "title") ?? "", f1, b1, new RectangleF(60, cy - 120, W - 120, 110), sf);
            g.DrawString(S(sc, "subtitle") ?? "", f2, b2, new RectangleF(60, cy - 5, W - 120, 120), sf);
        }
        using (var f3 = new Font(FONT, 18, FontStyle.Regular, GraphicsUnit.Pixel))
        using (var b3 = new SolidBrush(Color.FromArgb(170, 255, 255, 255)))
            g.DrawString("made by 資訊老師黃博胤", f3, b3, W - 230, H + BAND - 40);
    }

    static void DrawBand(Graphics g, Dictionary<string, object> sc, double t)
    {
        using (var br = new SolidBrush(NAVY)) g.FillRectangle(br, 0, H, W, BAND);
        using (var br = new SolidBrush(AMBER)) g.FillRectangle(br, 0, H, W, 5);
        string cap = S(sc, "caption"), sub = S(sc, "sub"), step = S(sc, "step");
        foreach (var c in L(sc, "captions")) if (t >= G(c, "t", 0)) { cap = S(c, "caption") ?? cap; sub = S(c, "sub") ?? sub; }
        float x = 40;
        if (!string.IsNullOrEmpty(step))
        {
            using (var br = new SolidBrush(AMBER)) g.FillEllipse(br, 36, H + BAND / 2 - 36, 72, 72);
            using (var f = new Font(FONT, 40, FontStyle.Bold, GraphicsUnit.Pixel))
            using (var br = new SolidBrush(NAVY))
            {
                var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
                g.DrawString(step, f, br, new RectangleF(36, H + BAND / 2 - 36, 72, 74), sf);
            }
            x = 132;
        }
        float a = (float)Clamp01(t / 0.4);
        using (var f1 = new Font(FONT, 36, FontStyle.Bold, GraphicsUnit.Pixel))
        using (var f2 = new Font(FONT, 25, FontStyle.Regular, GraphicsUnit.Pixel))
        using (var b1 = new SolidBrush(Color.FromArgb((int)(255 * a), Color.White)))
        using (var b2 = new SolidBrush(Color.FromArgb((int)(255 * a), 199, 210, 254)))
        {
            if (string.IsNullOrEmpty(sub)) g.DrawString(cap ?? "", f1, b1, x, H + BAND / 2 - 26);
            else
            {
                g.DrawString(cap ?? "", f1, b1, x, H + 22);
                g.DrawString(sub, f2, b2, x + 2, H + 78);
            }
        }
        using (var f3 = new Font(FONT, 15, FontStyle.Regular, GraphicsUnit.Pixel))
        using (var b3 = new SolidBrush(Color.FromArgb(120, 255, 255, 255)))
            g.DrawString("made by 資訊老師黃博胤", f3, b3, W - 190, H + BAND - 26);
    }

    // 整個畫面變暗（可留一個亮的洞）
    static void DrawDim(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        int a = (int)(G(b, "alpha", 120) * Clamp01(lt / 0.25));
        using (var reg = new Region(new Rectangle(0, 0, W, H)))
        {
            if (b.ContainsKey("hole")) { var h = L(b, "hole"); }
            if (b.ContainsKey("x")) reg.Exclude(new RectangleF((float)G(b, "x", 0), (float)G(b, "y", 0), (float)G(b, "w", 0), (float)G(b, "h", 0)));
            using (var br = new SolidBrush(Color.FromArgb(a, 0, 0, 0))) g.FillRegion(br, reg);
        }
    }

    // Win+Shift+S 截圖：畫面變暗＋頂端工具列＋拖曳出亮的選取框
    static void DrawSnip(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        double ds = G(b, "dragStart", 1), de = G(b, "dragEnd", 2);
        float x0 = (float)G(b, "x0", 0), y0 = (float)G(b, "y0", 0), x1 = (float)G(b, "x1", 0), y1 = (float)G(b, "y1", 0);
        float p = (float)Ease((lt - ds) / (de - ds));
        RectangleF sel = RectangleF.Empty;
        if (lt >= ds) sel = new RectangleF(x0, y0, (x1 - x0) * p, (y1 - y0) * p);
        using (var reg = new Region(new Rectangle(0, 0, W, H)))
        {
            if (sel.Width > 1) reg.Exclude(sel);
            using (var br = new SolidBrush(Color.FromArgb((int)(140 * Clamp01(lt / 0.25)), 0, 0, 0))) g.FillRegion(br, reg);
        }
        if (sel.Width > 1) using (var pen = new Pen(Color.White, 2)) g.DrawRectangle(pen, sel.X, sel.Y, sel.Width, sel.Height);
        // 頂端截圖工具列（示意）
        var bar = new RectangleF(W / 2 - 150, 14, 300, 50);
        using (var path = Round(bar, 10)) using (var br = new SolidBrush(Color.FromArgb(240, 243, 243, 243))) g.FillPath(br, path);
        string[] icons = { "▭", "✎", "▣", "⛶", "✕" };
        using (var f = new Font("Segoe UI Symbol", 20, GraphicsUnit.Pixel)) using (var br = new SolidBrush(Color.FromArgb(40, 40, 40)))
            for (int i = 0; i < icons.Length; i++)
            {
                if (i == 0) using (var hb = new SolidBrush(Color.FromArgb(200, 210, 230, 255))) g.FillRectangle(hb, bar.X + 12, bar.Y + 7, 44, 36);
                g.DrawString(icons[i], f, br, bar.X + 20 + i * 56, bar.Y + 11);
            }
    }

    static void DrawBox(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        var r = new RectangleF((float)G(b, "x", 0), (float)G(b, "y", 0), (float)G(b, "w", 0), (float)G(b, "h", 0));
        string style = S(b, "style") ?? "red";
        float a = (float)Clamp01(lt / 0.25);
        if (style == "gray-x")
        {
            using (var br = new SolidBrush(Color.FromArgb((int)(160 * a), 255, 255, 255))) g.FillRectangle(br, r);
            using (var pen = new Pen(Color.FromArgb((int)(230 * a), 100, 116, 139), 5))
            {
                pen.DashStyle = DashStyle.Dash;
                g.DrawRectangle(pen, r.X, r.Y, r.Width, r.Height);
                pen.DashStyle = DashStyle.Solid;
                g.DrawLine(pen, r.X, r.Y, r.Right, r.Bottom); g.DrawLine(pen, r.Right, r.Y, r.X, r.Bottom);
            }
        }
        else if (style == "select")
        {
            float grow = (float)G(b, "grow", 0);
            float p = grow > 0 ? (float)Clamp01(lt / grow) : 1f;
            using (var br = new SolidBrush(Color.FromArgb(110, 66, 133, 244))) g.FillRectangle(br, r.X, r.Y, r.Width * p, r.Height);
        }
        else if (style == "highlight")
        {
            using (var br = new SolidBrush(Color.FromArgb((int)(90 * a), 250, 204, 21))) g.FillRectangle(br, r);
            using (var pen = new Pen(Color.FromArgb((int)(255 * a), RED), 4)) using (var path = Round(r, 8)) g.DrawPath(pen, path);
        }
        else
        {
            using (var pen = new Pen(Color.FromArgb((int)(255 * a), RED), 5)) using (var path = Round(r, 10)) g.DrawPath(pen, path);
        }
    }

    // 紅圈：0.5 秒畫出來
    static void DrawCircle(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        float pad = (float)G(b, "pad", 14);
        var r = new RectangleF((float)G(b, "x", 0) - pad, (float)G(b, "y", 0) - pad, (float)G(b, "w", 0) + pad * 2, (float)G(b, "h", 0) + pad * 2);
        float sweep = (float)(360 * Ease(lt / 0.5));
        using (var pen = new Pen(RED, 6) { StartCap = LineCap.Round, EndCap = LineCap.Round })
            if (sweep > 1) g.DrawArc(pen, r, -100f, sweep);
    }

    static void DrawLabel(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        float a = (float)Clamp01(lt / 0.25);
        string text = S(b, "text");
        float size = (float)G(b, "size", 26);
        using (var f = new Font(FONT, size, FontStyle.Bold, GraphicsUnit.Pixel))
        {
            var sz = g.MeasureString(text, f);
            var r = new RectangleF((float)G(b, "x", 0), (float)G(b, "y", 0), sz.Width + 24, sz.Height + 12);
            Color bg = S(b, "color") == "green" ? Color.FromArgb(16, 185, 129) : (S(b, "color") == "gray" ? Color.FromArgb(71, 85, 105) : RED);
            using (var path = Round(r, 10)) using (var br = new SolidBrush(Color.FromArgb((int)(245 * a), bg))) g.FillPath(br, path);
            using (var br = new SolidBrush(Color.FromArgb((int)(255 * a), Color.White))) g.DrawString(text, f, br, r.X + 12, r.Y + 6);
        }
    }

    // 打字效果：在指定位置逐字出現（可選白底蓋掉原本內容）
    static void DrawTyping(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        string text = S(b, "text");
        double speed = G(b, "cps", 12);
        int n = Math.Min(text.Length, (int)(lt * speed) + 1);
        float x = (float)G(b, "x", 0), y = (float)G(b, "y", 0);
        if (b.ContainsKey("bgw"))
            using (var br = new SolidBrush(Color.White)) g.FillRectangle(br, x - 2, y - 2, (float)G(b, "bgw", 0), (float)G(b, "bgh", 30));
        using (var f = new Font(FONT, (float)G(b, "size", 20), FontStyle.Regular, GraphicsUnit.Pixel))
        using (var br = new SolidBrush(Color.FromArgb(30, 41, 59)))
        {
            string s = text.Substring(0, n);
            g.DrawString(s, f, br, x, y);
            if (((int)(lt * 2)) % 2 == 0 || n < text.Length)
            {
                var sz = g.MeasureString(s, f);
                using (var pen = new Pen(Color.FromArgb(30, 41, 59), 2)) g.DrawLine(pen, x + sz.Width - 2, y + 3, x + sz.Width - 2, y + f.Size + 2);
            }
        }
    }

    // 按鍵提示（畫面上方中央的鍵帽）
    static void DrawKeys(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        var keys = new List<string>(); foreach (var k in (IEnumerable)b["keys"]) keys.Add(k.ToString());
        float a = (float)Clamp01(lt / 0.2);
        float pop = (float)(1 + 0.12 * Math.Max(0, 1 - lt / 0.25));
        using (var f = new Font("Segoe UI", 34 * pop, FontStyle.Bold, GraphicsUnit.Pixel))
        using (var fp = new Font("Segoe UI", 30, FontStyle.Bold, GraphicsUnit.Pixel))
        {
            var widths = new List<float>(); float total = 0;
            foreach (var k in keys) { float w = g.MeasureString(k, f).Width + 40; widths.Add(w); total += w; }
            total += (keys.Count - 1) * 44;
            float x = (float)G(b, "x", W / 2) - total / 2, y = (float)G(b, "y", 90);
            using (var bg = new SolidBrush(Color.FromArgb((int)(170 * a), 15, 23, 42)))
            using (var path = Round(new RectangleF(x - 24, y - 18, total + 48, 96), 18)) g.FillPath(bg, path);
            for (int i = 0; i < keys.Count; i++)
            {
                var r = new RectangleF(x, y, widths[i], 60);
                using (var sh = new SolidBrush(Color.FromArgb((int)(255 * a), 148, 163, 184))) using (var p1 = Round(new RectangleF(r.X, r.Y + 5, r.Width, r.Height), 10)) g.FillPath(sh, p1);
                using (var kb = new SolidBrush(Color.FromArgb((int)(255 * a), Color.White))) using (var p2 = Round(r, 10)) g.FillPath(kb, p2);
                using (var tb = new SolidBrush(Color.FromArgb((int)(255 * a), 15, 23, 42)))
                {
                    var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
                    g.DrawString(keys[i], f, tb, r, sf);
                }
                x += widths[i];
                if (i < keys.Count - 1)
                {
                    using (var pb = new SolidBrush(Color.FromArgb((int)(255 * a), Color.White)))
                    {
                        var sf = new StringFormat { Alignment = StringAlignment.Center, LineAlignment = StringAlignment.Center };
                        g.DrawString("+", fp, pb, new RectangleF(x, y, 44, 60), sf);
                    }
                    x += 44;
                }
            }
        }
    }

    static void DrawToast(Graphics g, Dictionary<string, object> b, double t)
    {
        double lt; if (!Live(b, t, out lt)) return;
        float slide = (float)(1 - Ease(lt / 0.35));
        var r = new RectangleF(W - 400 + slide * 420, H - 120, 380, 96);
        using (var path = Round(r, 10)) using (var br = new SolidBrush(Color.FromArgb(245, 32, 32, 32))) g.FillPath(br, path);
        using (var f1 = new Font(FONT, 20, FontStyle.Bold, GraphicsUnit.Pixel))
        using (var f2 = new Font(FONT, 16, FontStyle.Regular, GraphicsUnit.Pixel))
        using (var b1 = new SolidBrush(Color.White)) using (var b2 = new SolidBrush(Color.FromArgb(200, 200, 200)))
        {
            g.DrawString(S(b, "title") ?? "", f1, b1, r.X + 20, r.Y + 18);
            g.DrawString(S(b, "text") ?? "", f2, b2, r.X + 20, r.Y + 52);
        }
    }

    static void DrawClick(Graphics g, Dictionary<string, object> b, double t)
    {
        double st = G(b, "t", 0), lt = t - st;
        if (lt < 0 || lt > 0.5) return;
        float x = (float)G(b, "x", 0), y = (float)G(b, "y", 0), rad = (float)(10 + 40 * lt / 0.5);
        int a = (int)(220 * (1 - lt / 0.5));
        using (var pen = new Pen(Color.FromArgb(a, RED), 4)) g.DrawEllipse(pen, x - rad, y - rad, rad * 2, rad * 2);
        using (var br = new SolidBrush(Color.FromArgb(a / 2, 250, 204, 21))) g.FillEllipse(br, x - rad * 0.6f, y - rad * 0.6f, rad * 1.2f, rad * 1.2f);
    }

    // 游標：關鍵影格之間緩動移動；mode=cross 時畫十字游標、hide 時不畫
    static void DrawCursor(Graphics g, List<Dictionary<string, object>> kf, double t)
    {
        if (kf.Count == 0) return;
        Dictionary<string, object> a = kf[0], bk = null;
        for (int i = 0; i < kf.Count; i++) { if (G(kf[i], "t", 0) <= t) a = kf[i]; else { bk = kf[i]; break; } }
        double x = G(a, "x", 0), y = G(a, "y", 0);
        if (bk != null && G(a, "t", 0) <= t)
        {
            double ta = G(a, "t", 0), tb = G(bk, "t", 0);
            double p = Ease((t - ta) / (tb - ta));
            x += (G(bk, "x", 0) - x) * p; y += (G(bk, "y", 0) - y) * p;
        }
        string mode = S(a, "mode") ?? "arrow";
        if (mode == "hide") return;
        float fx = (float)x, fy = (float)y;
        if (mode == "ibeam")
        {
            using (var pen = new Pen(Color.White, 5)) { g.DrawLine(pen, fx, fy - 13, fx, fy + 13); g.DrawLine(pen, fx - 6, fy - 14, fx + 6, fy - 14); g.DrawLine(pen, fx - 6, fy + 14, fx + 6, fy + 14); }
            using (var pen = new Pen(Color.Black, 2)) { g.DrawLine(pen, fx, fy - 13, fx, fy + 13); g.DrawLine(pen, fx - 5, fy - 14, fx + 5, fy - 14); g.DrawLine(pen, fx - 5, fy + 14, fx + 5, fy + 14); }
            return;
        }
        if (mode == "cross")
        {
            using (var pen = new Pen(Color.White, 5)) { g.DrawLine(pen, fx - 16, fy, fx + 16, fy); g.DrawLine(pen, fx, fy - 16, fx, fy + 16); }
            using (var pen = new Pen(Color.Black, 2)) { g.DrawLine(pen, fx - 15, fy, fx + 15, fy); g.DrawLine(pen, fx, fy - 15, fx, fy + 15); }
            return;
        }
        float s = 1.6f;
        PointF[] pts = {
            new PointF(0,0), new PointF(0,17), new PointF(4,13), new PointF(7,20), new PointF(10,19), new PointF(7,12), new PointF(12,12)
        };
        for (int i = 0; i < pts.Length; i++) pts[i] = new PointF(fx + pts[i].X * s, fy + pts[i].Y * s);
        using (var sh = new SolidBrush(Color.FromArgb(70, 0, 0, 0)))
        {
            var sp = (PointF[])pts.Clone(); for (int i = 0; i < sp.Length; i++) sp[i] = new PointF(sp[i].X + 3, sp[i].Y + 3);
            g.FillPolygon(sh, sp);
        }
        g.FillPolygon(Brushes.White, pts);
        using (var pen = new Pen(Color.Black, 1.8f) { LineJoin = LineJoin.Round }) g.DrawPolygon(pen, pts);
    }

    // 模擬的瀏覽器分頁列＋網址列（上方 80px），分頁可依時間切換、網址列可顯示「整條選取」
    static void DrawChrome(Graphics g, Dictionary<string, object> c, double t)
    {
        var tabs = new List<string>(); foreach (var o in (IEnumerable)c["tabs"]) tabs.Add(o.ToString());
        var urls = new List<string>(); foreach (var o in (IEnumerable)c["urls"]) urls.Add(o.ToString());
        int active = (int)G(c, "active", 0);
        foreach (var a in L(c, "activeAt")) if (t >= G(a, "t", 0)) active = (int)G(a, "active", 0);
        using (var br = new SolidBrush(Color.FromArgb(222, 225, 230))) g.FillRectangle(br, 0, 0, W, 42);
        using (var f = new Font(FONT, 14, FontStyle.Regular, GraphicsUnit.Pixel))
            for (int i = 0; i < tabs.Count; i++)
            {
                var r = new RectangleF(10 + i * 262, 6, 256, 36);
                if (i == active) using (var p = Round(new RectangleF(r.X, r.Y, r.Width, r.Height + 12), 10)) g.FillPath(Brushes.White, p);
                else if (i < tabs.Count - 1 && i + 1 != active) using (var pen = new Pen(Color.FromArgb(150, 150, 150))) g.DrawLine(pen, r.Right, r.Y + 9, r.Right, r.Bottom - 9);
                Color ic = tabs[i].Contains("文件") ? Color.FromArgb(66, 133, 244) : Color.FromArgb(180, 40, 40);
                using (var br = new SolidBrush(ic)) g.FillRectangle(br, r.X + 14, r.Y + 11, 14, 16);
                using (var br = new SolidBrush(Color.FromArgb(i == active ? 30 : 90, i == active ? 30 : 90, i == active ? 30 : 90)))
                    g.DrawString(tabs[i], f, br, new RectangleF(r.X + 36, r.Y + 9, r.Width - 46, 20), new StringFormat { Trimming = StringTrimming.EllipsisCharacter, FormatFlags = StringFormatFlags.NoWrap });
            }
        g.FillRectangle(Brushes.White, 0, 42, W, 38);
        using (var pen = new Pen(Color.FromArgb(218, 220, 224))) g.DrawLine(pen, 0, 79, W, 79);
        using (var f = new Font("Segoe UI Symbol", 18, GraphicsUnit.Pixel)) using (var br = new SolidBrush(Color.FromArgb(95, 99, 104)))
            g.DrawString("←   →   ⟳", f, br, 14, 48);
        var omni = new RectangleF(120, 46, W - 200, 30);
        using (var p = Round(omni, 15)) using (var br = new SolidBrush(Color.FromArgb(241, 243, 244))) g.FillPath(br, p);
        string url = urls[Math.Min(active, urls.Count - 1)];
        bool sel = false;
        foreach (var s in L(c, "urlSel")) { double lt; if (Live(s, t, out lt)) sel = true; }
        using (var f = new Font("Segoe UI", 15, GraphicsUnit.Pixel))
        {
            var sz = g.MeasureString(url, f);
            if (sel) using (var br = new SolidBrush(Color.FromArgb(168, 199, 250))) g.FillRectangle(br, omni.X + 16, omni.Y + 5, sz.Width - 4, 20);
            using (var br = new SolidBrush(Color.FromArgb(32, 33, 36))) g.DrawString(url, f, br, omni.X + 16, omni.Y + 5);
        }
    }

    static GraphicsPath Round(RectangleF r, float rad)
    {
        var p = new GraphicsPath(); float d = rad * 2;
        if (r.Width < d || r.Height < d) { p.AddRectangle(r); return p; }
        p.AddArc(r.X, r.Y, d, d, 180, 90); p.AddArc(r.Right - d, r.Y, d, d, 270, 90);
        p.AddArc(r.Right - d, r.Bottom - d, d, d, 0, 90); p.AddArc(r.X, r.Bottom - d, d, d, 90, 90);
        p.CloseFigure(); return p;
    }
}
