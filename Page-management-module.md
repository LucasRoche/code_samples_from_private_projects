# General architecture

The PageManager class is responsible for page creation, deletion, and display. It is created by the MainController and kept in the app main thread. The PageManager uses its child class the PageRouter to handle navigation, using signals sent by the pages and the other modules.

Each page is handled by a single [MVC](https://doc.qt.io/qt-5/model-view-programming.html) units.
Each MVC unit is composed of the following elements:
* The Controller is responsible for View creation, and signal linking between the View and Model(s)
* The View class is used for display. It does not manipulate data, only requests it from the model, and displays the result.
* The Model(s) class handles the data, send it to the views, and modify it if requested. The models are created by the MainController, and pointers to them are passed to the PageManager, then to the Controllers.

When a page is requested, the PageManager creates the page controller, passing along the necessary model pointers. The controller then creates the view. Lastly, the PageManager links the view signals to the PageRouter for navigation, and displays it if requested.

Each page is identified by a unique string (pageID), a static class variable defined in each view. The pageID list is created in the PageID class, in order to simplify the inclusion dependencies between modules (all modules and views include pageid.h and only need this header to use all page identificators).

![MVC diagram](https://user-images.githubusercontent.com/30040094/147246882-5508519a-65bb-4980-a2e4-b9f20e7a5238.png)

# Navigation

Navigation between the pages is handled by the PageRouter. Each page can send three different signals to the PageRouter:
* Previous(pageID): ask for the previous page to be displayed
* Next(pageID, nextPageID=""): ask for the next page to be displayed, optionally passing the ID of the next page as argument
* Send(pageID, json): send information to another module, the message will be transmitted by the PageRouter
Additionally, modules can request pages to be displayed, by sending a signal to the PageRouter

Upon receiving a navigation signal, the PageRouter emits a signal to the PageManager indicating which action must be performed:
* Instantiate(pageID): creates a new instance of the page which id corresponds to pageID
* Push(pageID): Displays the wanted page, if no instances have been created yet, call instantiate and then display
* Delete(pageID): Deletes the page

The PageRouter stores the history of pageID in a list, used to know which page should be displayed when calling previous.


# Steps for new page creation
1. Creates a controller class for the page, inheriting ControllerTemplate
2. Creates a view class for the page, inheriting ViewTemplate
3. Add a pageID static variable to the PageID class
4. Add a newpageview* class variable in the controller named view (should only be named view otherwise the pageManager can't handle it correctly)
5. Add a connection for clean MVC destruction (connect(view, SIGNAL(destroyed()), this, SLOT(onViewDestroyed()));)
6. Add statements in the PageRouter::reactOnNext, reactOnPrevious and/or reactOnSend
7. Add a statement in the PageManager::instantiate for the page creation



