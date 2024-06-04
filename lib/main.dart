import 'package:blink/pages/logland/landing.dart';
import 'package:flutter/material.dart';
import 'custom_bottom_nav_bar.dart';

void main() {
  runApp(Landing());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      
      debugShowCheckedModeBanner: false,
      home:
      Scaffold(body:MyHomePage(title: 'Blink'),) 
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
          title: Text(widget.title),
          leading: const Padding(
            padding: EdgeInsets.only(left: 25),
            child: Icon(Icons.person_2_rounded),
          ),
          actions: const [Padding(
            padding: EdgeInsets.only(right: 25),
            child: Icon(Icons.notification_add_rounded,),
          )],
          backgroundColor: const Color.fromRGBO(238, 238, 238, 100),
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
