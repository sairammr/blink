import 'package:blink/pages/logland/landing.dart';
import 'package:flutter/material.dart';
import 'custom_bottom_nav_bar.dart';

void main() {
  runApp(const Landing());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      
      debugShowCheckedModeBanner: false,
      home:
      Scaffold(body:MyHomePage(title: 'B L I N K'),) 
    );
  }
}

class MyHomePage extends StatefulWidget {
  final String title;

  MyHomePage({Key? key, required this.title}) : super(key: key);

  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Scaffold(
        appBar:
        
         AppBar(
  toolbarHeight: 80,
  title: Center(
    child: Text(
      widget.title,
      style: const TextStyle(color: Color.fromARGB(255, 116, 18, 39), fontSize: 30, fontWeight: FontWeight.bold),
    ),
  ),
  leading: const Padding(
    padding: EdgeInsets.only(left: 25),
    child: Icon(
      Icons.person_2_rounded,
      color: Color.fromARGB(193, 131, 22, 46),
      size: 30,
    ),
  ),
  actions: const [
    Padding(
      padding: EdgeInsets.only(right: 25),
      child: Icon(
        Icons.notification_add_rounded,
        color: Color.fromARGB(193, 131, 22, 46),
        size: 30,
      ),
    ),
  ],
  backgroundColor: const Color.fromARGB(0, 238, 238, 238),
  bottom: PreferredSize(
    preferredSize: const Size.fromHeight(7.0), // The height of the line
    child: Container(
          margin: const EdgeInsets.symmetric(horizontal: 17),
          color: Colors.grey, // The color of the line
          height: 2.0,
           // The thickness of the line
        ),
      
    
  ),
),

        body: const CustomBottomNavBar(),
      ),
    );
  }
}
class Landing extends StatelessWidget {
  const Landing({super.key});

  @override
  Widget build(BuildContext context) {

    return const MaterialApp(
      debugShowCheckedModeBanner: false,
      home: LandingPage(),
    );
  }
}
