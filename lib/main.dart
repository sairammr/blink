import 'package:flutter/material.dart';
import 'custom_bottom_nav_bar.dart';

void main() {
  runApp(MyApp());
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
          leading: Padding(
            padding: const EdgeInsets.only(left: 25),
            child: Icon(Icons.person_2_rounded),
          ),
          actions: [Padding(
            padding: const EdgeInsets.only(right: 25),
            child: Icon(Icons.notification_add_rounded,),
          )],
          backgroundColor: Color.fromARGB(255, 209, 142, 142),
        ),
        body: const CustomBottomNavBar(),
      ),
    );
  }
}
