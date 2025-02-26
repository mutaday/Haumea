import sys
import gi 
import psutil
import collections
import cairo
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio
from gi.repository import GLib

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app_ = self.get_application()
        self.set_default_size(400, 200)

        # Constants
        # Initialize list with 60 zero values for CPU usage
        # Initialize the default grid spacing and offset
        self.cpu_data = [0] * 60
        self.mem_data = [0] * 60
        self.grid_spacing = 70
        self.grid_offset = 0



        # self.headerbar = Gtk.HeaderBar.new()
        # self.set_titlebar(self.headerbar)
        # add_random_label_button = Gtk.Button.new_from_icon_name("applications-science")
        # add_random_label_button.connect("clicked",self.on_add_random_label_button_clicked)
        # add_random_label_button.set_tooltip_text("Add Random Label")
        # self.headerbar.pack_start(add_random_label_button)
                                                 
        self.main_box = Gtk.Box.new( Gtk.Orientation.HORIZONTAL,0) #(orientation VERTICAL|HORIZONTAL  , spacing in pixels)
        self.set_child(self.main_box)

        
        self.stack = Gtk.Stack.new()
        self.stack.props.hexpand = True
        self.stack.props.vexpand = True
        categories = ("Processes","Performance", "App history", "Startup apps", "Users", "Details", "Services")

        for category in categories:
            sw  = Gtk.ScrolledWindow.new()
            # box = Gtk.Box.new( Gtk.Orientation.VERTICAL,0)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            sw.set_child(box)
            self.stack.add_titled(sw,category,category) # Widget,name,title to show in Gtk.StackSidebar
            
        stack_switcher_sidebar =  Gtk.StackSidebar.new()
        stack_switcher_sidebar.props.hexpand = False
        stack_switcher_sidebar.props.vexpand = False
        stack_switcher_sidebar.set_stack(self.stack)
        
        self.main_box.append(stack_switcher_sidebar)
        self.main_box.append(self.stack)

        visible_box        = self.stack.get_visible_child().get_child().get_child() # Gtk.ScrolledWindow ===> get_child ====> Gtk.Viewport ===> get_child ====> Gtk.Box
        visible_child_name = self.stack.get_visible_child_name() # name look at self.stack.add_titled
        print(visible_box)
        print(visible_child_name)
        
        visible_box.append(Gtk.Label.new(visible_child_name))
        


        performance_box = self.stack.get_child_by_name("Performance").get_child().get_child()


        performance_box.append(Gtk.Label.new("Performance"))













    # GG
        # self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        # self.set_child(self.box)

        # NOTE: Will ditch the expand and go more responsive
        # TODO: Find a way to do this more responsively
        self.cpu_chart_area = Gtk.DrawingArea()
        self.cpu_chart_area.set_content_width(300)
        # self.cpu_chart_area.set_vexpand(True)
        # self.cpu_chart_area.set_hexpand(True)
        self.cpu_chart_area.set_content_height(200)

        self.cpu_chart_area.set_draw_func(self.cpu_chart)


        self.mem_chart_area = Gtk.DrawingArea()
        self.mem_chart_area.set_content_width(300)
        self.mem_chart_area.set_content_height(200)

        self.mem_chart_area.set_draw_func(self.mem_chart)
        performance_box.append(self.cpu_chart_area)
        performance_box.append(self.mem_chart_area)

        # NOTE: These value names are temporary
        lab_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        lab_box.set_valign(Gtk.Align.CENTER)
        lab_box.set_halign(Gtk.Align.CENTER)
        lab = Gtk.Label()
        lab.set_markup("<b>GPU Info</b>")
        lab_box.append(lab)
        performance_box.append(lab_box)

        GLib.timeout_add(1000, self.cpu_update)
        GLib.timeout_add(1000, self.mem_update)

    def cpu_update(self):
        usage = psutil.cpu_percent()
        self.cpu_data.append(usage)
        if len(self.cpu_data) > 60:
            self.cpu_data.pop(0)
        alloc = self.cpu_chart_area.get_width()
        num_v_lines = 20
        vertical_spacing = alloc / num_v_lines if alloc > 0 else 50

        self.grid_offset = (self.grid_offset + 10) % self.grid_spacing
        self.cpu_chart_area.queue_draw()
        return True


    def cpu_chart(self, drawing_area, cr, width, height):
        # print(psutil.virtual_memory().percent)

        # cr.set_source_rgb(1, 1, 1)
        # cr.paint()
        
        # TODO: Change values
        num_v_lines = 20
        vertical_spacing = width / num_v_lines
        num_h_lines = 20
        # Vertical grid lines
        cr.set_source_rgba(0.9, 0.9, 0.9, 0.1)
        x = -self.grid_offset
        while x < width:
            cr.move_to(x, 0)
            cr.line_to(x, height)
            x += vertical_spacing


        # Horizontal grid lines
        for i in range(1, num_h_lines):
            y = i * (height / num_h_lines)
            cr.move_to(0, y)
            cr.line_to(width, y)
        cr.stroke()
        
        # CPU usage line chart line path background
        cr.set_source_rgba(0.2, 0.6, 1.0, 0.2)
        cr.set_line_width(2)
        n = len(self.cpu_data)
        if n > 0:
            step = width / (n - 1)
            cr.move_to(0, height)
            for i, value in enumerate(self.cpu_data):
                x = i * step
                y = height - (value / 100 * height)
                cr.line_to(x, y)

            cr.line_to(width, height)
            cr.close_path()
            cr.fill()

        # CPU usage line chart lines
        # HACK: Maybe smoothen the lines a bit?
        # NOTE: Find a way to decrease the "sharpness"
        cr.set_source_rgb(0.2, 0.6, 1.0)
        cr.set_line_width(2)
        for i, value in enumerate(self.cpu_data):
            x = i * step
            y = height - (value / 100 * height)
            cr.line_to(x, y)
        cr.stroke()


    def mem_update(self):
        usage = psutil.virtual_memory().percent
        self.mem_data.append(usage)
        if len(self.mem_data) > 60:
            self.mem_data.pop(0)
        alloc = self.mem_chart_area.get_width()
        num_v_lines = 20
        vertical_spacing = alloc / num_v_lines if alloc > 0 else 50

        self.grid_offset = (self.grid_offset + 10) % self.grid_spacing
        self.mem_chart_area.queue_draw()
        return True

    def mem_chart(self, drawing_area, cr, width, height):
        # cr.set_source_rgb(1, 1, 1)
        # cr.paint()
        
        # TODO: Change values
        num_v_lines = 20
        vertical_spacing = width / num_v_lines
        num_h_lines = 20
        # Vertical grid lines
        cr.set_source_rgba(0.9, 0.9, 0.9, 0.1)
        x = -self.grid_offset
        while x < width:
            cr.move_to(x, 0)
            cr.line_to(x, height)
            x += vertical_spacing


        # Horizontal grid lines
        for i in range(1, num_h_lines):
            y = i * (height / num_h_lines)
            cr.move_to(0, y)
            cr.line_to(width, y)
        cr.stroke()
        
        # Memory usage line chart line path background
        cr.set_source_rgba(0.7, 0.5, 1.0, 0.2)
        cr.set_line_width(2)
        n = len(self.mem_data)
        if n > 0:
            step = width / (n - 1)
            cr.move_to(0, height)
            for i, value in enumerate(self.mem_data):
                x = i * step
                y = height - (value / 100 * height)
                cr.line_to(x, y)

            cr.line_to(width, height)
            cr.close_path()
            cr.fill()

        # Memory usage line chart lines
        # HACK: Maybe smoothen the lines a bit?
        # NOTE: Find a way to decrease the "sharpness"
        cr.set_source_rgb(0.7, 0.5, 1.0)
        cr.set_line_width(2)
        for i, value in enumerate(self.mem_data):
            x = i * step
            y = height - (value / 100 * height)
            cr.line_to(x, y)
        cr.stroke()

    # YY






        
class MyApp(Gtk.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def do_activate(self):
        active_window = self.props.active_window
        if active_window:
            active_window.present()
        else:
            self.win = MainWindow(application=self)
            self.win.present()

app = MyApp(application_id="com.github.yucefsourani.myapplicationexample",flags= Gio.ApplicationFlags.FLAGS_NONE)
app.run(sys.argv)
