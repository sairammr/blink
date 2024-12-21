// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables

import 'package:blink/components/todayGraph.dart';
import 'package:flutter/material.dart';

class SearchPage extends StatelessWidget {
  const SearchPage({super.key});

  @override
  Widget build(BuildContext context) {
   double width = MediaQuery.of(context).size.width;

    return Scaffold(
      body: SingleChildScrollView(
        child: Container(
                          margin: EdgeInsets.only(top : 19 , left : width * 0.04, right: width*0.04),

          decoration: BoxDecoration(
color :Color.fromRGBO(245, 214, 222, 1) ,
          
                  borderRadius: BorderRadius.all(Radius.circular(15))          ),
          child: Column(
            children: [
              Padding(
                    padding:  EdgeInsets.only(top :width*0.02,left:width*0.05,right:width*0.05 ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("Today",
                    style: TextStyle(fontSize: 24,
                    color: Color.fromRGBO(131, 22, 45, 1),
                    fontWeight: FontWeight.w600,
                    ),),
                    Row(
                      children: [
                        Icon(Icons.arrow_back_ios_new_rounded),
                        SizedBox(width: width*0.02,),
                        Icon(Icons.arrow_forward_ios_rounded)
                
                      ],
                    ),
                  ],
                ),
              ),

              TodayGraph()
            ],
          ),
        ),
      )
    );
  }
}

