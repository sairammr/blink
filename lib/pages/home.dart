import 'package:flutter/material.dart';
import 'package:simple_circular_progress_bar/simple_circular_progress_bar.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  List<String> days = ['Yesterday', 'Today', 'Tomorrow'];
  int current = 1;
  List<int> blink = [6, 7, 8];
  late ValueNotifier<double> valueNotifier;

  void back() {
    setState(() {
      current = (current - 1) % 3;
      if (current < 0) current += 3;
      valueNotifier.value = blink[current] * 10; // Ensure the index stays within the range
    });
  }

  void forward() {
    setState(() {
      current = (current + 1) % 3;
      valueNotifier.value = blink[current] * 10;
    });
  }

  @override
  void initState() {
    super.initState();
    valueNotifier = ValueNotifier(blink[current] * 10);
  }

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;

    return Scaffold(
      body: Column(
        children: [
          Container(
            margin: EdgeInsets.only(top: width * .03),
            height: width * .8,
            width: width * .8,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(25),
              color: Colors.red,
            ),
            child: Column(
              children: [
                Padding(
                  padding: EdgeInsets.symmetric(vertical: width * .05),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      InkWell(
                        onTap: back,
                        child: Icon(Icons.arrow_back_ios_new_rounded),
                      ),
                      Text(
                        days[current],
                        style: TextStyle(fontSize: 24, color: const Color.fromARGB(255, 0, 0, 0)),
                      ),
                      InkWell(
                        onTap: forward,
                        child: Icon(Icons.arrow_forward_ios_rounded),
                      ),
                    ],
                  ),
                ),
                SizedBox(height: width*.05,),
                SimpleCircularProgressBar(
                  size: width*.45,
                  valueNotifier: valueNotifier,
                  progressStrokeWidth: 24,
                  backStrokeWidth: 24,
                  mergeMode: true,
                  animationDuration: 2,
                  onGetText: (value) {
                    return Text(
                      '${value.toInt()/10.toInt()} Blinks ',
                      style: TextStyle(color: const Color.fromARGB(255, 0, 0, 0), fontSize: 20),
                    );
                  },
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
                margin: EdgeInsets.only(
                    top: width * .05, left: width * .1, right: width * .025),
                height: width * .375,
                width: width * .375,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(25),
                  color: Colors.red,
                ),
              ),
              Container(
                margin: EdgeInsets.only(
                    top: width * .05, right: width * .1, left: width * .025),
                height: width * .375,
                width: width * .375,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(25),
                  color: Colors.red,
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
