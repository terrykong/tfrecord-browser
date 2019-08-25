#!/usr/bin/env python
import subprocess
import urwid
import urwidtrees
import sys
from tfrecord_browser.tfrecord_helpers import bidirectional_tfrecord_iterator, smart_bidirectional_tfrecord_iterator, tfrecord_iterator

palette = [
    ('body', 'black', 'light gray'),
    ('focus', 'light gray', 'dark blue', 'standout'),
    ('bars', 'dark blue', 'light gray', ''),
    ('arrowtip', 'light blue', 'light gray', ''),
    ('connectors', 'light red', 'light gray', ''),
]

class FocusableText(urwid.WidgetWrap):
    """Selectable Text used for nodes in our example"""
    def __init__(self, txt):
        t = urwid.Text(txt)
        w = urwid.AttrMap(t, 'body', 'focus')
        urwid.WidgetWrap.__init__(self, w)

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

Text = FocusableText

def treenode_from_dict(name, d):
    if d is None:
        return None
    result = (Text(name), [])
    
    for k,v in d.items():
        result[1].append((Text("[{}]: {}".format(k,v)), None))
    return result

class UpDownTreeBox(urwidtrees.widgets.TreeBox):
    def __init__(self, treelist, iterator):
        self.treelist = treelist
        self.iterator = iterator
        self.index = 1
        super(UpDownTreeBox, self).__init__(
            urwidtrees.decoration.CollapsibleIndentedTree(
                urwidtrees.tree.SimpleTree([treelist]),
                #is_collapsed=lambda pos: False,
                icon_focussed_att='focus',
                # indent=6,
                # childbar_offset=1,
                # icon_frame_left_char=None,
                # icon_frame_right_char=None,
                # icon_expanded_char='-',
                # icon_collapsed_char='+',
            )
        )
        for _ in range(50):
            self.add_node_to_tree()
            self.index += 1
        self.refresh()

    def add_node_to_tree(self):
        if not self.treelist[1]:
             self.treelist[1] = []
        element, bytes = self.iterator.next()
        node = treenode_from_dict(name='example #{}'.format(self.index), d=element)
        if node:
             self.treelist[1].append(node)

    def keypress(self, size, key):
        cols, rows = size
        if key == 'r':
            # TODO: should add nodes to tree if num nodes < size of screen
            self.refresh()
        elif key == 'down':
            if self.treelist[1] and self.index < len(self.treelist[1]):
                # Don't need to add nodes if we've scrolled up
                continue
            self.add_node_to_tree()
            self.refresh()
            self.index += 1
        elif key == 'up':
            if self.index > 1:
                self.index -= 1
        focus = self.get_focus()[1]
            
        return super(UpDownTreeBox, self).keypress(size,key)

    def mouse_event(self, size, event, button, col, row, focus):
        cols, rows = size
        if int(button) == 4: # scroll up
            self.keypress(size, 'up')
        elif int(button) == 5: # scroll down
            self.keypress(size, 'down')
        return super(UpDownTreeBox, self).mouse_event(size, event, button, col, row, focus)


def main():
    if len(sys.argv) != 2:
        sys.stderr.write('No input file\n')
        sys.stderr.write('Usage: {} <tfrecord_path>\n'.format(sys.argv[0]))
        sys.exit(1)

    tfrecord_path = sys.argv[1]
    root_node = [Text(tfrecord_path), None]
    #tree_widget = UpDownTreeBox(root_node, bidirectional_tfrecord_iterator(tfrecord_path))
    #tree_widget = UpDownTreeBox(root_node, smart_bidirectional_tfrecord_iterator(tfrecord_path))
    tree_widget = UpDownTreeBox(root_node, tfrecord_iterator(tfrecord_path))
    rootwidget = urwid.AttrMap(tree_widget, 'body')
    footer = urwid.Columns([urwid.Text('Usage: q(quit) -(collapse) +(expand) r(refresh)'), urwid.Text('file=' + tfrecord_path + ' ', align='right')])
    
    def exit_on_q(key):
        if key in ['q', 'Q']:
            raise urwid.ExitMainLoop()
    
    loop = urwid.MainLoop(urwid.Frame(rootwidget,footer=footer), palette,
        unhandled_input=exit_on_q)
    
    loop.run()


if __name__ == "__main__":
    main()

