// ignore_for_file: prefer_const_constructors, prefer_const_literals_to_create_immutables

import 'package:flutter/material.dart';

class AddPage extends StatelessWidget {
  const AddPage({super.key});

  @override
  Widget build(BuildContext context) {
        double width = MediaQuery.of(context).size.width;

    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.only(bottom : 100),
            child: Column(children: [
            
              Container(
                alignment: Alignment.topLeft,
                padding: EdgeInsets.only(left: 33,top:20),
                child: const Text("Profile",
                style: TextStyle(fontSize:28,
                 ),),
              ),
            
              Padding(
                padding: const EdgeInsets.only(top:5),
                child: Center(
                  child: Container(
                    height: 100,
                    width: 100,
                    decoration : const BoxDecoration(color: Color.fromARGB(157, 131, 22, 46),
                    borderRadius: BorderRadius.all(Radius.circular(50))) 
                  ),
                ),
              ),
            
              Container(
                alignment: Alignment.center,
                padding: EdgeInsets.only(top:14),
                child: const Text("SAIRAM M R",
                style: TextStyle(fontSize:28,
                 ),),
              ),
              SizedBox(height: 24,),
              Container(
                margin: EdgeInsets.only(top : 0 , left : width * 0.04, right: width*0.04),
                decoration: BoxDecoration(
                  color :Color.fromRGBO(245, 214, 222, 1) ,
                  borderRadius: BorderRadius.all(Radius.circular(15))
                ),
                child: Column(
                  
                  children: [
                    ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.call_rounded),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('mobile number ',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Text("8015592227",style: TextStyle(fontSize:18 ),),
                          ),
                          Divider(color: Color.fromRGBO(131, 22, 45, 0.49),),
                          ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.mail_rounded),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('email id ',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Text("chris@gmail.com",style: TextStyle(fontSize:18 ),),
                          ),
                  ],
                ),
              ),
              SizedBox(height: width*0.04,),
              Container(
                margin: EdgeInsets.only(top : 0 , left : width * 0.04, right: width*0.04),
                decoration: BoxDecoration(
                  color :Color.fromRGBO(245, 214, 222, 1) ,
                  borderRadius: BorderRadius.all(Radius.circular(15))
                ),
                child: Column(
                  
                  children: [
                    ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left :10),
                              child: Icon(Icons.manage_accounts_rounded),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('Account ',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Icon(Icons.arrow_forward_ios_rounded)),
                                              Divider(color: Color.fromRGBO(131, 22, 45, 0.49),),
            
                          ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.sunny),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('Theme',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Icon(Icons.arrow_forward_ios_rounded),),
                          
                                        Divider(color: Color.fromRGBO(131, 22, 45, 0.49),),
            
                          ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.privacy_tip_rounded),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('Privacy ',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Icon(Icons.arrow_forward_ios_rounded),),
                          
                          Divider(color: Color.fromRGBO(131, 22, 45, 0.49),),
                          ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.notifications),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('Notification ',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Icon(Icons.arrow_forward_ios_rounded)),
                          
                                              Divider(color: Color.fromRGBO(131, 22, 45, 0.49),),
            
                          ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.mode_standby),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('Mode',style: TextStyle(fontSize:18 )),
                            ),
                            trailing: Icon(Icons.arrow_forward_ios_rounded)),
                          
                  ],
                ),
              ),
                      SizedBox(height: width * 0.04,),
              Container(
                margin: EdgeInsets.only(top : 0 , left : width * 0.04, right: width*0.04),
                decoration: BoxDecoration(
                  color :Color.fromRGBO(245, 214, 222, 1) ,
                  borderRadius: BorderRadius.all(Radius.circular(15))
                ),
                child: Column(
                  
                  children: [
                    ListTile(
                            leading: Padding(
                              padding: const EdgeInsets.only(left : 10),
                              child: Icon(Icons.logout_rounded),
                            ),
                            
                            title: Padding(
                              padding: const EdgeInsets.only(left: 10),
                              child: Text('Logout ',style: TextStyle(fontSize:18 )),
                            ),
                          ),
                          
                  ],
                ),
              ),
            ],),
          ),
        ),
      )
    );
  }
}
