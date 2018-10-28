SEARCH_DIR(.)
__DYNAMIC  =  0;

MEMORY
{
    imem    : ORIGIN = 0x00000000, LENGTH = 0x8000
}

SECTIONS
{
    .vectors :
    {
        . = ALIGN(4);
        KEEP(*(.vectors))
    } > imem

    .text : {
        . = ALIGN(4);
        *(.text)
    }  > imem
}