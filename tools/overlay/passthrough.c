#include <X11/Xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/shape.h>	// Region creation
#include <X11/extensions/Xfixes.h>	// Applying it
#include <stdio.h>	// printf
#include <unistd.h>	// getpid() hack

// compile:
//     gcc passthrough.c -o passthrough.so -shared -fPIC -lX11 -lXfixes

// notes:
//     http://stackoverflow.com/questions/14788439/getting-x11-window-handle-from-gtkwidget/14788489
//         #include <gtk/gtk.h>
//         `pkg-config --cflags --libs gtk+-2.0`
//     http://stackoverflow.com/questions/2858263/how-do-i-bring-a-processes-window-to-the-foreground-on-x-windows-c
//         Deals with pointer to window conversion

void enumWindows(Display *display, Window rootWindow, Atom _atomPID) {
	Atom           type;
	int            format;
	unsigned long  nItems, bytesAfter;
	unsigned char *propPID;
	
	XGetWindowProperty(display, rootWindow, _atomPID, 0, 1, False, XA_CARDINAL, &type, &format, &nItems, &bytesAfter, &propPID);
	
	if(propPID) {
		long pid = *((unsigned long *) propPID);
		if(pid == getpid()) {
// 			printf("YAY\n");
			XserverRegion region = XFixesCreateRegion(display, NULL, 0);
			XFixesSetWindowShapeRegion(display, rootWindow, ShapeBounding, 0, 0, 0);
			XFixesSetWindowShapeRegion(display, rootWindow, ShapeInput, 0, 0, region);
			XFixesDestroyRegion(display, region);
		}
		XFree(propPID);
	}
	
	Window parent, *children;
	unsigned int noOfChildren;
	int status = XQueryTree(display, rootWindow, &rootWindow, &parent, &children, &noOfChildren);

	if(status && noOfChildren) {
		int i;
		for(i = 0; i < noOfChildren; i++) {
			enumWindows(display, children[i], _atomPID);
		}
		XFree(children);
	}
}

void allow_input_passthrough(int hwnd) {
// 	printf("My process ID : %d\n", getpid());
// 	printf("Called with: 0x%x\n", hwnd);
	
	Display* display = XOpenDisplay(NULL);
	Atom atom = XInternAtom(display, "_NET_WM_PID", True);
	Window rootwin = DefaultRootWindow(display);
	enumWindows(display, rootwin, atom);
}