#include <pybind11/embed.h>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <dlfcn.h>
#include <unordered_map>
#include <iostream>
#include <memory>
#include <sys/time.h>

//typedef unsigned char uint8_t;
//typedef unsigned int uint32_t; 
//typedef uint8_t svScalar;
//typedef svScalar svBit;
//typedef uint32_t svBitVecVal;

namespace py=pybind11;

py::scoped_interpreter guard;

// Include common routines
#include <verilated.h>

// Include model header, generated from Verilating "top.v"
#include "Vbfm.h"

#include <iostream>

using namespace std;

unsigned char *payload_data = nullptr;
unsigned char *data = nullptr;

// extern void c_py_gen_packet(unsigned char *data);

void send_tlm_data(Vbfm* top_, int num) 
{
    // c_py_gen_packet(data);
    py::module_ sys = py::module_::import("sys");
    py::list path = sys.attr("path");
    path.attr("append")("../utils");    //for verilator
    // path.attr("append")("./utils");    //for galaxsim
    py::module_ utils = py::module_::import("harness_utils");   

    py::bytes result = utils.attr("send_data")();
    Py_ssize_t size = PyBytes_GET_SIZE(result.ptr());
    unsigned char * payload_data = (unsigned char * )PyBytes_AsString(result.ptr());    //# low bit 01 02 03 ... 20 high bit

    // cout << "send_tlm_data" << endl;
    memcpy(&top_->data, payload_data, num*2);
}


int main(int argc, char* argv[]) {

    std::unique_ptr<VerilatedContext> contextp_;
    Vbfm* top_;

    contextp_ = std::make_unique<VerilatedContext>();
    top_ = new Vbfm(contextp_.get());
    
    Verilated::traceEverOn(true);

    int NUM = 20000;    //send times
    int item_num = 100;
    int num = 0;

    // Simulate until $finish
    while (!Verilated::gotFinish()) {       
             
        //item_num 表示每个tlm包含的数的个数; 除以2后表示每个tlm包含的激励组数
        send_tlm_data(top_, item_num);
        top_->xmit_en = 1;
        while(top_->xmit_en == 1)
        {
            top_->eval();
            contextp_->timeInc(5000);
        } 
        num = num + 1;
        if(num >= NUM) break;
    }
    return 0;
}