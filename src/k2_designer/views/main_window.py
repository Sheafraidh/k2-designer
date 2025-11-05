"""
Main application window with MDI interface.
"""

from PyQt6.QtWidgets import (QMainWindow, QMdiArea, QDockWidget, QVBoxLayout, 
                             QHBoxLayout, QWidget, QMenuBar, QToolBar, QStatusBar,
                             QFileDialog, QMessageBox, QSplitter, QTabWidget, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QKeySequence, QAction

from ..models import Project
from ..controllers.project_manager import ProjectManager
from ..dialogs import DomainDialog, OwnerDialog, TableDialog
from .object_browser import ObjectBrowser
from .properties_panel import PropertiesPanel
from .diagram_view import DiagramView


class MainWindow(QMainWindow):
    """Main application window with tabbed diagram interface."""
    
    # Signals
    project_changed = pyqtSignal(Project)
    
    def __init__(self):
        super().__init__()
        self.project_manager = ProjectManager()
        self.current_project: Project = None
        self.open_diagrams = {}  # Dictionary to track open diagram tabs {diagram: tab_index}
        self._setup_ui()
        self._create_actions()
        self._create_menus()
        self._create_toolbars()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the main UI components."""
        self.setWindowTitle("K2 Designer")
        self.setMinimumSize(1200, 800)
        
        # Central widget with tab widget for diagrams
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        
        # Create welcome/empty state widget
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.addStretch()
        
        welcome_label = QLabel("No diagrams open\n\nCreate a new diagram or open an existing one from the Object Browser")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: gray; font-size: 14px;")
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addStretch()
        
        self.tab_widget.addTab(welcome_widget, "Welcome")
        self.tab_widget.setTabsClosable(False)  # Don't allow closing welcome tab initially
        
        self.setCentralWidget(self.tab_widget)
        
        # Object browser dock
        self.object_browser = ObjectBrowser()
        self.object_dock = QDockWidget("Object Browser", self)
        self.object_dock.setWidget(self.object_browser)
        self.object_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                        Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.object_dock)
        
        # Properties panel dock
        self.properties_panel = PropertiesPanel()
        self.properties_dock = QDockWidget("Properties", self)
        self.properties_dock.setWidget(self.properties_panel)
        self.properties_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | 
                                           Qt.DockWidgetArea.RightDockWidgetArea)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.properties_dock)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_actions(self):
        """Create all menu and toolbar actions."""
        # File actions
        self.new_action = QAction("&New Project", self)
        self.new_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileIcon))
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.new_action.setStatusTip("Create a new project")
        self.new_action.triggered.connect(self._new_project)
        
        self.open_action = QAction("&Open Project", self)
        self.open_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DirOpenIcon))
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_action.setStatusTip("Open an existing project")
        self.open_action.triggered.connect(self._open_project)
        
        self.save_action = QAction("&Save Project", self)
        self.save_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.setStatusTip("Save the current project")
        self.save_action.triggered.connect(self._save_project)
        
        self.save_as_action = QAction("Save Project &As...", self)
        self.save_as_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.setStatusTip("Save the project with a new name")
        self.save_as_action.triggered.connect(self._save_project_as)
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogCloseButton))
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.setStatusTip("Exit the application")
        self.exit_action.triggered.connect(self.close)
        
        # View actions
        self.new_diagram_action = QAction("New &Diagram", self)
        self.new_diagram_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogNewFolder))
        self.new_diagram_action.setStatusTip("Create a new diagram")
        self.new_diagram_action.triggered.connect(self._new_diagram)
        
        # Tools actions
        self.generate_action = QAction("&Generate SQL", self)
        self.generate_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_FileDialogDetailedView))
        self.generate_action.setStatusTip("Generate SQL scripts for database objects")
        self.generate_action.triggered.connect(self._generate_sql)
        
        # Window actions
        self.close_all_action = QAction("Close &All Diagrams", self)
        self.close_all_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogCloseButton))
        self.close_all_action.setStatusTip("Close all open diagram tabs")
        self.close_all_action.triggered.connect(self._close_all_diagrams)
        
        self.next_tab_action = QAction("&Next Diagram", self)
        self.next_tab_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowRight))
        self.next_tab_action.setShortcut("Ctrl+Tab")
        self.next_tab_action.setStatusTip("Switch to next diagram tab")
        self.next_tab_action.triggered.connect(self._next_tab)
        
        self.prev_tab_action = QAction("&Previous Diagram", self)
        self.prev_tab_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowLeft))
        self.prev_tab_action.setShortcut("Ctrl+Shift+Tab")
        self.prev_tab_action.setStatusTip("Switch to previous diagram tab")
        self.prev_tab_action.triggered.connect(self._prev_tab)
        
        # Help actions
        self.about_action = QAction("&About", self)
        self.about_action.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
        self.about_action.setStatusTip("Show application information")
        self.about_action.triggered.connect(self._about)
    
    def _create_menus(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        tools_menu.addAction(self.generate_action)
        
        # View menu
        view_menu = menubar.addMenu("&View")
        view_menu.addAction(self.new_diagram_action)
        view_menu.addSeparator()
        view_menu.addAction(self.object_dock.toggleViewAction())
        view_menu.addAction(self.properties_dock.toggleViewAction())
        
        # Window menu
        window_menu = menubar.addMenu("&Window")
        window_menu.addAction(self.next_tab_action)
        window_menu.addAction(self.prev_tab_action)
        window_menu.addSeparator()
        window_menu.addAction(self.close_all_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_action)
    
    def _create_toolbars(self):
        """Create toolbars."""
        # Main toolbar
        main_toolbar = self.addToolBar("Main")
        main_toolbar.addAction(self.new_action)
        main_toolbar.addAction(self.open_action)
        main_toolbar.addAction(self.save_action)
        main_toolbar.addSeparator()
        main_toolbar.addAction(self.generate_action)
    
    def _connect_signals(self):
        """Connect signals between components."""
        # Connect object browser selection to properties panel
        self.object_browser.selection_changed.connect(
            self.properties_panel.set_object
        )
        
        # Connect properties panel modifications to refresh object browser
        self.properties_panel.object_modified.connect(
            self._on_object_modified
        )
        
        # Connect project changes
        self.project_changed.connect(self.object_browser.set_project)
        
        # Connect tab widget signals
        self.tab_widget.tabCloseRequested.connect(self._close_diagram_tab)
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
    
    def _on_object_modified(self, obj):
        """Handle when an object is modified in the properties panel."""
        # Refresh the object browser to show updated information
        self.object_browser._refresh_tree()
        
        # Refresh all open diagrams to show updated object information
        self._refresh_all_diagrams()
    
    def _refresh_all_diagrams(self):
        """Refresh all open diagram tabs to show updated object information."""
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if widget and hasattr(widget, 'diagram') and hasattr(widget, 'scene'):
                # This is a diagram view, refresh it
                widget.refresh_diagram()
    
    def _on_diagram_selection_changed(self, obj):
        """Handle when selection changes in a diagram."""
        if obj:
            # Find and select the corresponding item in the object browser
            self.object_browser.select_object(obj)
    
    def _on_diagram_multiple_selection_changed(self, objects):
        """Handle when multiple objects are selected in a diagram."""
        if len(objects) == 1:
            # Single object - use existing single selection logic
            self.properties_panel.set_object(objects[0])
            self.object_browser.select_object(objects[0])
        elif len(objects) > 1:
            # Multiple objects - show multiple selection in properties panel
            self.properties_panel.set_object(objects)
            # Clear object browser selection for multiple selections
            self.object_browser.tree_widget.clearSelection()
        else:
            # No objects selected
            self.properties_panel.set_object(None)
            self.object_browser.tree_widget.clearSelection()
    
    def _new_project(self):
        """Create a new project."""
        if not self._check_unsaved_changes():
            return
        
        from ..dialogs import NewProjectDialog
        dialog = NewProjectDialog(parent=self)
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            project_name = dialog.get_project_name()
            project_description = dialog.get_project_description()
            
            self.current_project = self.project_manager.new_project(project_name, project_description)
            self.project_changed.emit(self.current_project)
            self._update_window_title()
            self.status_bar.showMessage(f"New project '{project_name}' created")
    
    def _open_project(self):
        """Open an existing project."""
        if not self._check_unsaved_changes():
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project", "", "K2 Designer Projects (*.k2p);;All Files (*)"
        )
        
        if file_path:
            try:
                project = self.project_manager.load_project(file_path)
                if project:
                    self.current_project = project
                    self.project_changed.emit(self.current_project)
                    self._update_window_title()
                    self.status_bar.showMessage(f"Project opened: {file_path}")
                    
                    # Open last active diagram if available
                    self._open_last_active_diagram()
                else:
                    QMessageBox.critical(
                        self, "Error", "Failed to load project file."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to open project:\n{str(e)}"
                )
    
    def _save_project(self):
        """Save the current project."""
        if not self.current_project:
            return
        
        if not self.current_project.file_path:
            self._save_project_as()
        else:
            try:
                if self.project_manager.save_project():
                    self.status_bar.showMessage(f"Project saved: {self.current_project.file_path}")
                else:
                    QMessageBox.critical(
                        self, "Error", "Failed to save project."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save project:\n{str(e)}"
                )
    
    def _save_project_as(self):
        """Save the project with a new name."""
        if not self.current_project:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project As", "", "K2 Designer Projects (*.k2p);;All Files (*)"
        )
        
        if file_path:
            try:
                if self.project_manager.save_project(file_path):
                    self._update_window_title()
                    self.status_bar.showMessage(f"Project saved: {file_path}")
                else:
                    QMessageBox.critical(
                        self, "Error", "Failed to save project."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to save project:\n{str(e)}"
                )
    
    def _new_diagram(self):
        """Create a new diagram."""
        if not self.current_project:
            QMessageBox.warning(
                self, "No Project", "Please open or create a project first."
            )
            return
        
        from ..dialogs import DiagramDialog
        from ..models import Diagram
        
        existing_names = [diagram.name for diagram in self.current_project.diagrams]
        dialog = DiagramDialog(existing_names=existing_names, parent=self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            diagram = dialog.create_diagram()
            self.current_project.add_diagram(diagram)
            self.object_browser._refresh_tree()
            self._open_diagram(diagram)
    
    def _generate_sql(self):
        """Open the SQL generation dialog."""
        if not self.current_project:
            QMessageBox.warning(
                self, "No Project", "Please open or create a project first."
            )
            return
        
        from ..dialogs import GenerateDialog
        
        dialog = GenerateDialog(self.current_project, parent=self)
        dialog.exec()
    
    def _open_diagram(self, diagram):
        """Open a specific diagram in a new tab."""
        if not self.current_project or not diagram:
            return
        
        # Check if diagram is already open in a tab
        if diagram in self.open_diagrams:
            # Diagram is already open, just switch to its tab
            tab_index = self.open_diagrams[diagram]
            self.tab_widget.setCurrentIndex(tab_index)
            
            # Set this diagram as active
            self.current_project.set_active_diagram(diagram.name)
            
            # Refresh object browser to show active state
            self.object_browser._refresh_tree()
            return
        
        # Diagram is not open, create new tab
        # Set this diagram as active
        self.current_project.set_active_diagram(diagram.name)
        
        # Create diagram view
        diagram_view = DiagramView(self.current_project, diagram)
        
        # Store diagram reference in the view for easy access
        diagram_view.diagram = diagram
        
        # Connect diagram selection to properties panel and object browser
        diagram_view.selection_changed.connect(
            self.properties_panel.set_object
        )
        diagram_view.selection_changed.connect(
            self._on_diagram_selection_changed
        )
        
        # Connect multiple selection signal to properties panel
        diagram_view.multiple_selection_changed.connect(
            self._on_diagram_multiple_selection_changed
        )
        
        # Remove welcome tab if it's the only tab
        if self.tab_widget.count() == 1 and self.tab_widget.tabText(0) == "Welcome":
            self.tab_widget.removeTab(0)
            self.open_diagrams.clear()  # Clear any tracking
        
        # Add the diagram tab
        tab_index = self.tab_widget.addTab(diagram_view, diagram.name)
        self.open_diagrams[diagram] = tab_index
        
        # Switch to the new tab
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Enable tab closing now that we have diagram tabs
        self.tab_widget.setTabsClosable(True)
        
        # Refresh object browser to show active state
        self.object_browser._refresh_tree()
    
    def _close_diagram_tab(self, index):
        """Close a diagram tab."""
        if index < 0 or index >= self.tab_widget.count():
            return
        
        # Get the diagram view widget
        diagram_view = self.tab_widget.widget(index)
        if not diagram_view or not hasattr(diagram_view, 'diagram'):
            return
        
        diagram = diagram_view.diagram
        
        # Remove from tracking
        if diagram in self.open_diagrams:
            del self.open_diagrams[diagram]
        
        # Update tab indices for remaining tabs
        self._update_tab_indices()
        
        # Remove the tab
        self.tab_widget.removeTab(index)
        
        # If no more diagram tabs, show welcome tab
        if self.tab_widget.count() == 0:
            self._show_welcome_tab()
        
        # Refresh object browser to update active diagram state
        self.object_browser._refresh_tree()
    
    def _on_tab_changed(self, index):
        """Handle tab change to update active diagram."""
        if index < 0 or index >= self.tab_widget.count():
            return
        
        # Get the current diagram view
        diagram_view = self.tab_widget.widget(index)
        if diagram_view and hasattr(diagram_view, 'diagram'):
            # Set as active diagram
            self.current_project.set_active_diagram(diagram_view.diagram.name)
            # Refresh object browser to show active state
            self.object_browser._refresh_tree()
    
    def _update_tab_indices(self):
        """Update the tab indices in the open_diagrams tracking dictionary."""
        new_open_diagrams = {}
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if widget and hasattr(widget, 'diagram'):
                new_open_diagrams[widget.diagram] = i
        self.open_diagrams = new_open_diagrams
    
    def _show_welcome_tab(self):
        """Show the welcome tab when no diagrams are open."""
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.addStretch()
        
        welcome_label = QLabel("No diagrams open\n\nCreate a new diagram or open an existing one from the Object Browser")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: gray; font-size: 14px;")
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addStretch()
        
        self.tab_widget.addTab(welcome_widget, "Welcome")
        self.tab_widget.setTabsClosable(False)  # Don't allow closing welcome tab
    
    def _close_all_diagrams(self):
        """Close all open diagram tabs."""
        # Close all tabs except welcome tab
        while self.tab_widget.count() > 0:
            diagram_view = self.tab_widget.widget(0)
            if hasattr(diagram_view, 'diagram'):
                self._close_diagram_tab(0)
            else:
                # This is the welcome tab, remove it
                self.tab_widget.removeTab(0)
        
        # Clear tracking and show welcome tab
        self.open_diagrams.clear()
        self._show_welcome_tab()
    
    def _next_tab(self):
        """Switch to the next tab."""
        current = self.tab_widget.currentIndex()
        next_index = (current + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
    
    def _prev_tab(self):
        """Switch to the previous tab."""
        current = self.tab_widget.currentIndex()
        prev_index = (current - 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(prev_index)
    
    def _open_last_active_diagram(self):
        """Open the last active diagram if it exists."""
        if not self.current_project:
            return
        
        # Try to find the last active diagram
        last_active = None
        if self.current_project.last_active_diagram:
            last_active = self.current_project.get_diagram(self.current_project.last_active_diagram)
        
        # If no last active diagram, try to find any active diagram
        if not last_active:
            last_active = self.current_project.get_active_diagram()
        
        # If still no active diagram and there are diagrams, open the first one
        if not last_active and self.current_project.diagrams:
            last_active = self.current_project.diagrams[0]
        
        # Open the diagram if found
        if last_active:
            self._open_diagram(last_active)
    
    def _check_unsaved_changes(self) -> bool:
        """Check for unsaved changes and prompt user."""
        # TODO: Implement unsaved changes detection
        return True
    
    def _update_window_title(self):
        """Update the main window title."""
        if self.current_project:
            title = f"K2 Designer - {self.current_project.name}"
            if self.current_project.file_path:
                title += f" ({self.current_project.file_path})"
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("K2 Designer")
    
    def _about(self):
        """Show about dialog."""
        QMessageBox.about(
            self, "About K2 Designer",
            "K2 Designer v1.0.0\n\n"
            "A visual database design tool for creating ER diagrams and managing database schemas."
        )
    
    def closeEvent(self, event):
        """Handle application close event."""
        if self._check_unsaved_changes():
            event.accept()
        else:
            event.ignore()