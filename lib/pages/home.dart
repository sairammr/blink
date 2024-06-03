import 'package:flutter/material.dart';
import 'package:simple_circular_progress_bar/simple_circular_progress_bar.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    List Days=['Yesterday','Today',"Tomorrow"];
    int current=1;
    double width=MediaQuery.of(context).size.width;
    double height=MediaQuery.of(context).size.height;
    return Scaffold(
      body: Column(
        children: [
          Container(
            margin: EdgeInsets.only(top: width*.03),
            height: width*.8,
            width: width*.8,
            decoration: BoxDecoration(borderRadius: BorderRadius.circular(25),
              color: Colors.red,
            ),
            child: Column(
            
              children: [
                Padding(
                  padding:  EdgeInsets.symmetric(vertical: width*.05),
                  child: Row(
                  
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                    Icon(Icons.arrow_back_ios_new_rounded),
                    Text(Days[current],),
                    Icon(Icons.arrow_forward_ios_rounded),
                  ],),
                ),
                SimpleCircularProgressBar(
                  
                    progressColors: const [
                        Colors.cyan,
                        Colors.green,
                        Colors.amberAccent,
                        Colors.redAccent,
                        Colors.purpleAccent
                    ],
                    backColor: Colors.blueGrey,
                ),
              ],
            ),

          ),
          Row(
            crossAxisAlignment: CrossAxisAlignment.center,

            children: [
            Container(
            margin: EdgeInsets.only(top: width*.05,left: width*.1,right: width*.025),
            height: width*.375,
            width: width*.375,
            decoration: BoxDecoration(borderRadius: BorderRadius.circular(25),
              color: Colors.red,
            ),
          ),Container(
            margin: EdgeInsets.only(top: width*.05,right: width*.1,left: width*.025),
            height: width*.375,
            width: width*.375,
            decoration: BoxDecoration(borderRadius: BorderRadius.circular(25),
              color: Colors.red,
            ),
          ),
          ],)
        ],
      ),
    );
  }
}
