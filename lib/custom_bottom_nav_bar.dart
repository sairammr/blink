import 'package:blink/pages/home.dart';
import 'package:blink/pages/profile.dart';
import 'package:blink/pages/stats.dart';
import 'package:flutter/material.dart';
import 'package:flutter/gestures.dart';
import 'package:flutter_floating_bottom_bar/flutter_floating_bottom_bar.dart';


class CustomBottomNavBar extends StatefulWidget {
  const CustomBottomNavBar({super.key});

  @override
  State<CustomBottomNavBar> createState() => _CustomBottomNavBarState();
}

class _CustomBottomNavBarState extends State<CustomBottomNavBar> with SingleTickerProviderStateMixin {
  late int currentPage;
  late TabController tabController;
  final List<Color> colors = [
    Color.fromARGB(255,255,255,255),
    Color.fromARGB(255,245,214,222),
    Color.fromARGB(255, 169, 29,58),
  ];

  @override
  void initState() {
    super.initState();
    currentPage = 0;
    tabController = TabController(length: 3, vsync: this);
    tabController.animation?.addListener(
      () {
        final value = tabController.animation!.value.round();
        if (value != currentPage && mounted) {
          changePage(value);
        }
      },
    );
  }

  void changePage(int newPage) {
    setState(() {
      currentPage = newPage;
    });
  }

  @override
  void dispose() {
    tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {

    return BottomBar(
      clip: Clip.none,
      fit: StackFit.expand,
      child: Stack(
        alignment: Alignment.center,
        clipBehavior: Clip.none,
        children: [
          TabBar(
            indicatorPadding: const EdgeInsets.fromLTRB(6, 0, 6, 0),
            controller: tabController,
            indicator: UnderlineTabIndicator(
              borderSide: BorderSide(
                color: currentPage <= 4 ? colors[currentPage] : colors[1],
                width: 4,
                
              ),
              insets: EdgeInsets.fromLTRB(12, 5, 12, 8),
            ),
            tabs: [
              SizedBox(
                height: 55,
                width: 40,
                child: Center(
                  child: Icon(
                    Icons.home,
                    color: currentPage == 0 ? colors[0] : colors[1],
                  ),
                ),
              ),
              SizedBox(
                height: 55,
                width: 40,
                child: Center(
                  child: Icon(
                    Icons.search,
                    color: currentPage == 1 ? colors[0] : colors[1],
                  ),
                ),
              ),
              SizedBox(
                height: 55,
                width: 40,
                child: Center(
                  child: Icon(
                    Icons.add,
                    color: currentPage == 2 ? colors[0] : colors[1],
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
      
      borderRadius: BorderRadius.circular(500),
      duration: Duration(milliseconds: 200),
      curve: Curves.decelerate,
      showIcon: true,
      width: MediaQuery.of(context).size.width * 0.6,
      barColor: colors[2],
      start: 2,
      end: 0,
      offset: 10,
      barAlignment: Alignment.bottomCenter,
      barDecoration: BoxDecoration(
        color: colors[currentPage],
        borderRadius: BorderRadius.circular(500),
      ),
      iconDecoration: BoxDecoration(
        color: colors[currentPage],
        borderRadius: BorderRadius.circular(500),
      ),
      hideOnScroll: true,
      scrollOpposite: false,
      onBottomBarHidden: () {},
      onBottomBarShown: () {},
      body: (context, controller) => TabBarView(
        controller: tabController,
        dragStartBehavior: DragStartBehavior.down,
        physics: const BouncingScrollPhysics(),
        children: [
          HomePage(),
          SearchPage(),
          AddPage(),
        ],
      ),
    );
  }
}
