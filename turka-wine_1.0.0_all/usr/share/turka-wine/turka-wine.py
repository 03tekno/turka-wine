import gi
import subprocess
import threading
import os

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib

class WineKurucu(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.apply_advanced_styling()
        self.set_title("Turka Wine Yöneticisi")
        self.set_default_size(800, 750)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        # --- ÜST KISIM (BUTONLAR) ---
        top_clamp = Adw.Clamp(maximum_size=800)
        top_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        top_clamp.set_child(top_box)
        
        list_box = Gtk.ListBox()
        list_box.add_css_class("boxed-list")
        list_box.set_margin_top(25)
        list_box.set_margin_bottom(15)
        
        # .NET Framework satırı buradan kaldırıldı
        self.add_manage_row(list_box, "Wine &amp; Sistem Hazırlığı", "Sistem paketlerini kurar veya kaldırır", self.start_wine_install, self.remove_wine_install)
        self.add_manage_row(list_box, "Winetricks &amp; Araçlar", "Winetricks kütüphane aracını yönetir", self.start_tricks_install, self.remove_tricks_install)
        
        # Wine Sıfırlama ve diğer araçlar
        self.add_row_simple(list_box, "Wine Yapılandırmasını Sıfırla", "Tüm Wine dosyalarını siler ve temiz bir başlangıç yapar", self.reset_wine_prefix, "Sıfırla")
        self.add_row_simple(list_box, "Sağ Tık Menüsüne Ekle", "EXE dosyaları için 'Wine ile Aç' seçeneğini onarır", self.fix_context_menu, "Onar")
        self.add_row_simple(list_box, "Wine Ayarları", "Wine yapılandırma panelini açar", lambda _: subprocess.Popen(["winecfg"]), "Aç")

        top_box.append(list_box)
        main_box.append(top_clamp)

        # --- ALT KISIM (LOG EKRANI) ---
        bottom_clamp = Adw.Clamp(maximum_size=800)
        bottom_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        bottom_clamp.set_child(bottom_box)

        log_label = Gtk.Label(label="İşlem Kayıtları ve Çıktılar", xalign=0)
        log_label.set_margin_top(15)
        log_label.set_margin_bottom(10)
        log_label.add_css_class("log-header")
        bottom_box.append(log_label)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.add_css_class("log-card")
        
        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_monospace(True)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        self.text_view.set_margin_top(15)
        self.text_view.set_margin_bottom(15)
        self.text_view.set_margin_start(15)
        self.text_view.set_margin_end(15)
        
        scrolled.set_child(self.text_view)
        bottom_box.append(scrolled)
        bottom_box.set_margin_bottom(35)
        
        main_box.append(bottom_clamp)
        self.buffer = self.text_view.get_buffer()

    def apply_advanced_styling(self):
        provider = Gtk.CssProvider()
        css = """
            window, .background { background-color: #f0f0f0; font-size: 17px; }
            list, .boxed-list { background-color: #ffffff; border: 1px solid #dcdcdc; }
            .log-card { background-color: #e8e8e8; border: 1px solid #cccccc; border-radius: 12px; }
            textview { background-color: #e8e8e8; font-size: 16px; }
            .log-header { font-size: 20px; font-weight: bold; color: #444444; }
            button { font-size: 16px; padding: 6px 14px; }
            button.suggested-action { background-color: #3584e4; color: #ffffff; font-weight: bold; }
            button.destructive-action { background-color: #e01b24; color: #ffffff; font-weight: bold; }
        """
        provider.load_from_data(css.encode())
        Gtk.StyleContext.add_provider_for_display(self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def add_manage_row(self, list_box, title, subtitle, install_cb, remove_cb):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        btn_box.set_valign(Gtk.Align.CENTER)
        
        ins_btn = Gtk.Button(label="Kur")
        ins_btn.add_css_class("suggested-action")
        ins_btn.connect("clicked", install_cb)
        
        rem_btn = Gtk.Button(label="Kaldır")
        rem_btn.add_css_class("destructive-action")
        rem_btn.connect("clicked", remove_cb)
        
        btn_box.append(ins_btn)
        btn_box.append(rem_btn)
        row.add_suffix(btn_box)
        list_box.append(row)

    def add_row_simple(self, list_box, title, subtitle, callback, btn_label):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        btn = Gtk.Button(label=btn_label, valign=Gtk.Align.CENTER, width_request=140)
        btn.connect("clicked", callback)
        row.add_suffix(btn)
        list_box.append(row)

    def write_to_log(self, text):
        GLib.idle_add(self._safe_log_write, text)

    def _safe_log_write(self, text):
        self.buffer.insert(self.buffer.get_end_iter(), text)
        mark = self.buffer.create_mark(None, self.buffer.get_end_iter(), False)
        self.text_view.scroll_to_mark(mark, 0.0, True, 0.5, 0.5)

    def run_cmd(self, command, use_sudo=True):
        def thread_func():
            self.write_to_log(f"\n[İŞLEM] > {command}\n" + "-"*40 + "\n")
            f_cmd = ["pkexec", "bash", "-c", command] if use_sudo else ["bash", "-c", command]
            p = subprocess.Popen(f_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            if p.stdout:
                for line in p.stdout:
                    self.write_to_log(line)
            p.wait()
            self.write_to_log(f"\n[BİTTİ]\n")
        threading.Thread(target=thread_func, daemon=True).start()

    def fix_context_menu(self, _):
        desktop_entry = """[Desktop Entry]
Type=Application
Name=Wine Windows Program Loader
Exec=wine %f
MimeType=application/x-ms-dos-executable;application/x-msi;application/x-ms-shortcut;
NoDisplay=true
Icon=wine
"""
        try:
            path = os.path.expanduser("~/.local/share/applications/wine.desktop")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(desktop_entry)
            self.run_cmd("update-desktop-database ~/.local/share/applications && xdg-mime default wine.desktop application/x-ms-dos-executable", use_sudo=False)
            self.write_to_log("\n[OK] Sağ tık menüsü onarıldı.\n")
        except Exception as e:
            self.write_to_log(f"\n[HATA] {str(e)}\n")

    def start_wine_install(self, _): self.run_cmd("dpkg --add-architecture i386 && apt update && apt install -y wine wine64 wine32 libwine:i386")
    def remove_wine_install(self, _): self.run_cmd("apt purge -y wine* libwine* && apt autoremove -y")
    def start_tricks_install(self, _): self.run_cmd("apt update && apt install -y winetricks zenity cabextract")
    def remove_tricks_install(self, _): self.run_cmd("apt purge -y winetricks")
    def reset_wine_prefix(self, _): self.run_cmd("rm -rf $HOME/.wine && rm -rf $HOME/.local/share/applications/wine && rm -rf $HOME/.local/share/applications/wine.desktop && wineboot -u", use_sudo=False)

class Application(Adw.Application):
    def __init__(self):
        super().__init__(application_id="turka.wine_v1")
    def do_activate(self):
        win = WineKurucu(application=self)
        win.present()

if __name__ == "__main__":
    app = Application()
    app.run(None)