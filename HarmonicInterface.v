// File: HarmonicInterface.v
// Generated by MyHDL 0.7
// Date: Thu Jun 16 18:27:27 2011


`timescale 1ns/10ps

module HarmonicInterface (
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
// Harmonic digital interface
// 
// clk     - input clock
// reset   - async reset to default values
// scl     - SPI clock
// cs      - SPI chip select
// din     - SPI MOSI
// dout    - SPI MISO
// 
// swXx     - multiplier switches
// cintXx   - Cap on
// zeroXx   - Reset cap to Vcm
// fastXx   - gm x10
// tuneXx   - 12bit IDAC word

input clk_in;
input reset_in;
input scl_in;
input cs_in;
input din;
output nco_i;
reg nco_i;
output nco_q;
reg nco_q;
input multA;
input multB;
output clk_out;
wire clk_out;
output reset_out;
wire reset_out;
output scl_out;
wire scl_out;
output cs_out;
wire cs_out;
output dout;
wire dout;
output [6:0] swAp;
reg [6:0] swAp;
output [6:0] swAn;
reg [6:0] swAn;
output cintAn;
reg cintAn;
output zeroAn;
reg zeroAn;
output fastAn;
reg fastAn;
output [11:0] tuneAn;
reg [11:0] tuneAn;
output cintAp;
reg cintAp;
output zeroAp;
reg zeroAp;
output fastAp;
reg fastAp;
output [11:0] tuneAp;
reg [11:0] tuneAp;
output [6:0] swBp;
reg [6:0] swBp;
output [6:0] swBn;
reg [6:0] swBn;
output cintBn;
reg cintBn;
output zeroBn;
reg zeroBn;
output fastBn;
reg fastBn;
output [11:0] tuneBn;
reg [11:0] tuneBn;
output cintBp;
reg cintBp;
output zeroBp;
reg zeroBp;
output fastBp;
reg fastBp;
output [11:0] tuneBp;
reg [11:0] tuneBp;

reg [47:0] cdata;
reg [6:0] sB;
reg [6:0] sA;
reg [15:0] nco_phase;
reg spiSlave_sample;
reg [47:0] spiSlave_reg;





always @(posedge clk_in) begin: HARMONICINTERFACE_SWITCHOUT
    swAn <= sA;
    swAp <= (~sA);
    swBn <= sB;
    swBp <= (~sB);
end


always @(multA, cdata[29], cdata[47]) begin: HARMONICINTERFACE_CHANNELA_LOGIC
    if ((cdata[47] == 0)) begin
        if ((cdata[29] == 0)) begin
            if (multA) begin
                sA = 48;
            end
            else begin
                sA = 72;
            end
        end
        else begin
            if (multA) begin
                sA = 33;
            end
            else begin
                sA = 65;
            end
        end
    end
    else begin
        if ((cdata[29] == 0)) begin
            sA = 6;
        end
        else begin
            sA = 5;
        end
    end
end



assign clk_out = clk_in;
assign reset_out = reset_in;
assign scl_out = scl_in;
assign cs_out = cs_in;


always @(posedge clk_in, negedge reset_in) begin: HARMONICINTERFACE_NCO_NCOLOGIC
    integer tmp;
    if ((reset_in == 0)) begin
        nco_phase <= 0;
        nco_i <= 0;
        nco_q <= 0;
    end
    else if ((cdata[46] == 0)) begin
        nco_phase <= 0;
        nco_i <= 0;
        nco_q <= 0;
    end
    else begin
        nco_phase <= ((nco_phase + cdata[46-1:32]) % 65536);
        tmp = ((nco_phase + 16384) % 65536);
        nco_i <= tmp[15];
        nco_q <= nco_phase[15];
    end
end


always @(cdata) begin: HARMONICINTERFACE_PASSTHRU
    cintAn <= cdata[31];
    cintAp <= (!cdata[31]);
    zeroAn <= cdata[30];
    zeroAp <= (!cdata[30]);
    fastAn <= cdata[28];
    fastAp <= (!cdata[28]);
    tuneAn <= cdata[28-1:16];
    tuneAp <= (~cdata[28-1:16]);
    cintBn <= cdata[15];
    cintBp <= (!cdata[15]);
    zeroBn <= cdata[14];
    zeroBp <= (!cdata[14]);
    fastBn <= cdata[12];
    fastBp <= (!cdata[12]);
    tuneBn <= cdata[12-1:0];
    tuneBp <= (~cdata[12-1:0]);
end


always @(posedge cs_in) begin: HARMONICINTERFACE_SPISLAVE_CHIPSELECT
    if ((cs_in == 1)) begin
        cdata <= spiSlave_reg;
    end
end


always @(negedge scl_in, negedge reset_in) begin: HARMONICINTERFACE_SPISLAVE_INPUTREGISTER
    if ((reset_in == 0)) begin
        spiSlave_reg <= 0;
    end
    else begin
        if ((cs_in == 0)) begin
            spiSlave_reg[48-1:1] <= spiSlave_reg[(48 - 1)-1:0];
            spiSlave_reg[0] <= spiSlave_sample;
        end
    end
end


always @(posedge scl_in) begin: HARMONICINTERFACE_SPISLAVE_SAMPLEINPUT
    spiSlave_sample <= din;
end



assign dout = spiSlave_reg[(48 - 1)];


always @(multB, cdata[13], cdata[47]) begin: HARMONICINTERFACE_CHANNELB_LOGIC
    if ((cdata[47] == 0)) begin
        if ((cdata[13] == 0)) begin
            if (multB) begin
                sB = 48;
            end
            else begin
                sB = 72;
            end
        end
        else begin
            if (multB) begin
                sB = 33;
            end
            else begin
                sB = 65;
            end
        end
    end
    else begin
        if ((cdata[13] == 0)) begin
            sB = 6;
        end
        else begin
            sB = 5;
        end
    end
end

endmodule