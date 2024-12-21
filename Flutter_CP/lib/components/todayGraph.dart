import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

class TodayGraph extends StatefulWidget {
  const TodayGraph({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _TodayGraphState createState() => _TodayGraphState();
}

class _TodayGraphState extends State<TodayGraph> {
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    // Simulate data fetching delay
    Future.delayed(const Duration(seconds: 2), () {
      setState(() {
        _isLoading = false;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    return _isLoading ? _buildLoading() : _buildChart();
  }

  Widget _buildLoading() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  Widget _buildChart() {
    return const SfCartesianChart();
  }
}
