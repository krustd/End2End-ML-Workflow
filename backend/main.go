package main

import (
	_ "template/internal/packed"

	"github.com/gogf/gf/v2/os/gctx"

	"template/internal/cmd"
)

func main() {
	cmd.Main.Run(gctx.GetInitCtx())
}
