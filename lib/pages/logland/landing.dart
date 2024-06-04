import 'package:blink/main.dart';
import 'package:blink/pages/home.dart';
import 'package:flutter/material.dart';
import 'package:page_transition/page_transition.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:flutter/services.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: LandingPage(),
  ));
}

class LandingPage extends StatefulWidget {
  const LandingPage({super.key});

  @override
  _LandingPageState createState() => _LandingPageState();
}

class _LandingPageState extends State<LandingPage> {
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 2), () {
      Navigator.push(
        context,
        PageTransition(
          duration: Duration(seconds: 1),
          type: PageTransitionType.bottomToTop, 
          child: const Landing2(),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: Color.fromRGBO(131, 22, 45, 1),  
    );
  }
}
class Landing2 extends StatefulWidget {
  const Landing2({Key? key}) : super(key: key);
  
  @override
  _Landing2State createState() => _Landing2State();
}

class _Landing2State extends State<Landing2> {
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 2), () {
      Navigator.pushReplacement(
        context,
        PageTransition(
          duration: const Duration(seconds: 1),
          type: PageTransitionType.bottomToTop, 
          child:  MyApp(),
        ),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    return WillPopScope(
      onWillPop: () async {
        // Disable back gesture
        return false;
      },
      child: Scaffold(
        backgroundColor: const Color.fromARGB(255, 236, 230, 230),
        body: Center(
          child: SvgPicture.asset(
            'assets/images/blink.svg',
            height: 200,
          ),
        ),
      ),
    );
  }
}
