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
#include "VAdd.h"

#include <iostream>

using namespace std;

unsigned char *payload_data = nullptr;
unsigned char *data = nullptr;

// extern void c_py_gen_packet(unsigned char *data);

void get_tlm_data(unsigned char* data, int num) 
{
    // c_py_gen_packet(data);
    py::module_ sys = py::module_::import("sys");
    py::list path = sys.attr("path");
    path.attr("append")("../utils");    //for verilator
    // path.attr("append")("./utils");    //for galaxsim
    py::module_ utils = py::module_::import("harness_utils");   

    py::bytes result = utils.attr("send_data")();
    Py_ssize_t size = PyBytes_GET_SIZE(result.ptr());
    unsigned char *payload_data = (unsigned char * )PyBytes_AsString(result.ptr());    //# low bit 01 02 03 ... 20 high bit
    memcpy(data, payload_data, num*2);
}


int main(int argc, char* argv[]) {

    std::unique_ptr<VerilatedContext> contextp_;
    VAdd* top;

    contextp_ = std::make_unique<VerilatedContext>();
    top = new VAdd(contextp_.get());
    
    Verilated::traceEverOn(true);

    int NUM = 20000;    //send times
    int item_num = 100;
    int num = 0;

    top->clk = 0;
    top->reset = 1;

    unsigned char *data = new unsigned char[200];
    bool flag = false;
    int main_time = 0;

    // Simulate until $finish
    while(!Verilated::gotFinish())
    {
        if(num>=2000000) break;
        if(num % 100 == 0) flag = false;
        if(main_time==100) top->reset=0;
        if(!flag) 
        {
            get_tlm_data(data, item_num);
            flag = true;
        }
        if(top->reset ==0)
        {
            top->clk = !(top->clk);
            if(top->clk==1) 
            {
                if(flag)
                {
                    top->io_A = data[(num*2)%200];
                    top->io_B = data[(num*2+1)%200];
                    //cout << "data:" << int(top->io_X)<<endl;
                    num = num + 1;
                }
            }
        }

        top->eval();
        //tfp->dump(main_time);
        main_time+=5;
    }

    //tfp->close();
    delete top;
    return 0;
}