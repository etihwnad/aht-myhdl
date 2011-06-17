`timescale 1ns/1ps
module tb_HarmonicInterface;

reg clk_in;
reg reset_in;
reg scl_in;
reg cs_in;
reg din;
wire nco_i;
wire nco_q;
reg multA;
reg multB;
wire clk_out;
wire reset_out;
wire scl_out;
wire cs_out;
wire dout;
wire [6:0] swAp;
wire [6:0] swAn;
wire cintAn;
wire zeroAn;
wire fastAn;
wire [11:0] tuneAn;
wire cintAp;
wire zeroAp;
wire fastAp;
wire [11:0] tuneAp;
wire [6:0] swBp;
wire [6:0] swBn;
wire cintBn;
wire zeroBn;
wire fastBn;
wire [11:0] tuneBn;
wire cintBp;
wire zeroBp;
wire fastBp;
wire [11:0] tuneBp;

initial begin
    $from_myhdl(
        clk_in,
        reset_in,
        scl_in,
        cs_in,
        din,
        multA,
        multB
    );
    $to_myhdl(
        nco_i,
        nco_q,
        clk_out,
        reset_out,
        scl_out,
        cs_out,
        dout,
        swAp,
        swAn,
        cintAn,
        zeroAn,
        fastAn,
        tuneAn,
        cintAp,
        zeroAp,
        fastAp,
        tuneAp,
        swBp,
        swBn,
        cintBn,
        zeroBn,
        fastBn,
        tuneBn,
        cintBp,
        zeroBp,
        fastBp,
        tuneBp
    );
end

HarmonicInterface dut(
    clk_in,
    reset_in,
    scl_in,
    cs_in,
    din,
    nco_i,
    nco_q,
    multA,
    multB,
    clk_out,
    reset_out,
    scl_out,
    cs_out,
    dout,
    swAp,
    swAn,
    cintAn,
    zeroAn,
    fastAn,
    tuneAn,
    cintAp,
    zeroAp,
    fastAp,
    tuneAp,
    swBp,
    swBn,
    cintBn,
    zeroBn,
    fastBn,
    tuneBn,
    cintBp,
    zeroBp,
    fastBp,
    tuneBp
);

endmodule
